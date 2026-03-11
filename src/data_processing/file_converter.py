"""
file_converter.py
-----------------
Handles ingestion of CSV, Excel, PDF, and TXT bank statement files
and converts them all to a standardised Pandas DataFrame.
"""

import io
import re
import logging
from pathlib import Path

import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

# ─── Converters ───────────────────────────────────────────────────────────────

def load_csv(file) -> pd.DataFrame:
    """Load a CSV file (path or file-like object)."""
    try:
        df = pd.read_csv(file, encoding="utf-8", on_bad_lines="skip")
    except UnicodeDecodeError:
        df = pd.read_csv(file, encoding="latin-1", on_bad_lines="skip")
    logger.info(f"CSV loaded: {df.shape[0]} rows, {df.shape[1]} columns")
    return df


def load_excel(file) -> pd.DataFrame:
    """Load an Excel (.xlsx / .xls) file."""
    df = pd.read_excel(file, engine="openpyxl")
    logger.info(f"Excel loaded: {df.shape[0]} rows, {df.shape[1]} columns")
    return df


def load_pdf(file) -> pd.DataFrame:
    """
    Extract transactions from a PDF bank statement using pdfplumber.
    Falls back to a regex-based line parser when tables are absent.
    """
    try:
        import pdfplumber
    except ImportError:
        logger.warning("pdfplumber not installed. Returning empty DataFrame for PDF.")
        return pd.DataFrame()

    rows = []
    # pdfplumber accepts both file paths and file-like objects
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            if tables:
                for table in tables:
                    for row in table:
                        if row and any(cell for cell in row):
                            rows.append(row)
            else:
                # Fallback: regex scan of plain text
                text = page.extract_text() or ""
                for line in text.split("\n"):
                    parsed = _parse_text_line(line)
                    if parsed:
                        rows.append(parsed)

    if not rows:
        logger.warning("No data extracted from PDF.")
        return pd.DataFrame()

    df = pd.DataFrame(rows)
    # Use first row as header if it looks like one
    if df.shape[0] > 1 and _is_header_row(df.iloc[0].tolist()):
        df.columns = df.iloc[0].str.strip()
        df = df.iloc[1:].reset_index(drop=True)

    logger.info(f"PDF loaded: {df.shape[0]} rows")
    return df


def load_txt(file) -> pd.DataFrame:
    """Parse a plain-text bank statement (pipe / tab / comma delimited)."""
    if hasattr(file, "read"):
        content = file.read()
        if isinstance(content, bytes):
            content = content.decode("utf-8", errors="ignore")
        lines = content.splitlines()
    else:
        with open(file, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()

    rows = []
    for line in lines:
        line = line.strip()
        if not line or len(line) < 10:
            continue
        parsed = _parse_text_line(line)
        if parsed:
            rows.append(parsed)

    if not rows:
        # Try treating as CSV
        content_str = "\n".join(lines)
        try:
            return pd.read_csv(io.StringIO(content_str), sep=None, engine="python")
        except Exception:
            return pd.DataFrame()

    df = pd.DataFrame(rows, columns=["Date", "Description", "Amount"])
    logger.info(f"TXT loaded: {df.shape[0]} rows")
    return df


# ─── Helpers ──────────────────────────────────────────────────────────────────

DATE_PATTERN = re.compile(
    r"(\d{2}[/-]\d{2}[/-]\d{4}|\d{4}[/-]\d{2}[/-]\d{2}|\d{2}\s+\w{3}\s+\d{4})"
)
AMOUNT_PATTERN = re.compile(r"[\d,]+\.\d{2}")


def _parse_text_line(line: str):
    """Try to extract (date, description, amount) from a free-form text line."""
    date_match = DATE_PATTERN.search(line)
    amount_matches = AMOUNT_PATTERN.findall(line)
    if not date_match or not amount_matches:
        return None
    date_str = date_match.group(1)
    amount_str = amount_matches[-1].replace(",", "")
    start, end = date_match.span()
    description = line[end:].strip()
    # Remove the amount from description
    description = description.replace(amount_matches[-1], "").strip(" -|,")
    return [date_str, description[:100], amount_str]


def _is_header_row(row) -> bool:
    """Heuristic: a row is a header if most cells are alphabetic strings."""
    if not row:
        return False
    alpha = sum(1 for c in row if c and str(c).replace(" ", "").isalpha())
    return alpha / len(row) > 0.5


# ─── Universal Loader ─────────────────────────────────────────────────────────

def load_file(file, filename: str = None) -> pd.DataFrame:
    """
    Auto-detect file type and load into a DataFrame.

    Parameters
    ----------
    file     : str | Path | file-like object
    filename : str – used when `file` is a bytes / file-like object without a name
    """
    # Resolve extension
    if filename:
        ext = Path(filename).suffix.lower()
    elif hasattr(file, "name"):
        ext = Path(file.name).suffix.lower()
    elif isinstance(file, (str, Path)):
        ext = Path(file).suffix.lower()
    else:
        ext = ".csv"  # assume CSV as last resort

    logger.info(f"Loading file with extension: {ext}")

    loaders = {
        ".csv": load_csv,
        ".xlsx": load_excel,
        ".xls": load_excel,
        ".pdf": load_pdf,
        ".txt": load_txt,
    }

    loader = loaders.get(ext, load_csv)
    return loader(file)
