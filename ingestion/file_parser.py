from pathlib import Path

import pandas as pd


def parse_file(file_path: str | Path) -> pd.DataFrame:
    """Read a CSV or XLSX file into a Pandas DataFrame.

    Args:
        file_path: Path to the file to read.

    Returns:
        A Pandas DataFrame containing the file contents.

    Raises:
        ValueError: If the file type is not supported.
        FileNotFoundError: If the file does not exist.
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    suffix = path.suffix.lower()

    if suffix == ".csv":
        return pd.read_csv(path)
    elif suffix in (".xls", ".xlsx"):
        return pd.read_excel(path)
    else:
        raise ValueError(f"Unsupported file type: {suffix}. Supported: .csv, .xlsx")


def parse_file_bytes(
    buffer: object,
    filename: str,
) -> pd.DataFrame:
    """Read CSV or XLSX bytes into a Pandas DataFrame.

    Args:
        buffer: A file-like object (e.g. BytesIO) containing the data.
        filename: The original filename to determine the file type.

    Returns:
        A Pandas DataFrame containing the file contents.

    Raises:
        ValueError: If the file type is not supported.
    """
    suffix = Path(filename).suffix.lower()

    if suffix == ".csv":
        return pd.read_csv(buffer)
    elif suffix == ".xlsx":
        return pd.read_excel(buffer, engine="openpyxl")
    elif suffix == ".xls":
        return pd.read_excel(buffer, engine="xlrd")
    else:
        raise ValueError(f"Unsupported file type: {suffix}. Supported: .csv, .xlsx")
