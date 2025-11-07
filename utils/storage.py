import csv
from dataclasses import dataclass
from typing import Dict, Iterable, List
import os

@dataclass
class DataPaths:
    transactions_csv: str
    queue_csv: str


def ensure_files(paths: DataPaths):
    """Create CSV files with headers if they don't exist."""
    os.makedirs(os.path.dirname(paths.transactions_csv), exist_ok=True)
    os.makedirs(os.path.dirname(paths.queue_csv), exist_ok=True)

    # Transactions file
    if not os.path.exists(paths.transactions_csv):
        with open(paths.transactions_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["first_name", "last_name", "ticket_type", "time", "status"])

    # Queue file
    if not os.path.exists(paths.queue_csv):
        with open(paths.queue_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["first_name", "last_name", "ticket_type", "time"])


def read_csv_as_dicts(path: str) -> List[Dict]:
    """Read a CSV and return list of dictionaries."""
    rows = []
    if not os.path.exists(path):
        return rows
    with open(path, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows


def append_transaction(path: str, row: Dict):
    """Add one transaction (confirmed or sold out) to the log."""
    file_exists = os.path.exists(path)
    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["first_name", "last_name", "ticket_type", "time", "status"])
        writer.writerow([
            row.get("first_name", ""),
            row.get("last_name", ""),
            row.get("ticket_type", ""),
            row.get("time", ""),
            row.get("status", ""),
        ])


def write_queue(path: str, rows: Iterable[Dict]):
    """Rewrite the entire queue (e.g., after processing someone)."""
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["first_name", "last_name", "ticket_type", "time"])
        for r in rows:
            writer.writerow([
                r.get("first_name", ""),
                r.get("last_name", ""),
                r.get("ticket_type", ""),
                r.get("time", ""),
            ])
