"""
Build the structured dance -> song -> genre -> culture dataset.

Reads the seed + collected records, validates every row against the schema,
and writes two synchronized exports:
  - data/dance_music_dataset.csv   (flat, app/spreadsheet friendly)
  - data/dance_music_dataset.json  (nested lists preserved)

Run:  python -m src.build_dataset
"""

import csv
import json
import os

from .schema import COLUMNS, validate
from .collect import collect

OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


def build(out_dir: str = OUT_DIR) -> dict:
    records = collect()

    # Validate first; a real run would reject or flag, not silently drop.
    problems = {}
    for r in records:
        issues = validate(r)
        if issues:
            problems[r.dance_id or r.dance_name] = issues
    if problems:
        print(f"[build] {len(problems)} rows have validation issues:")
        for k, v in problems.items():
            print(f"   {k}: {', '.join(v)}")

    os.makedirs(out_dir, exist_ok=True)
    csv_path = os.path.join(out_dir, "dance_music_dataset.csv")
    json_path = os.path.join(out_dir, "dance_music_dataset.json")

    with open(csv_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=COLUMNS)
        writer.writeheader()
        for r in records:
            writer.writerow(r.to_flat())

    with open(json_path, "w", encoding="utf-8") as fh:
        json.dump([r.to_json_obj() for r in records], fh, indent=2, ensure_ascii=False)

    # Lightweight summary so the operator can sanity-check coverage.
    by_cat = {}
    for r in records:
        by_cat[r.category] = by_cat.get(r.category, 0) + 1

    summary = {
        "total_rows": len(records),
        "by_category": by_cat,
        "csv": csv_path,
        "json": json_path,
        "validation_issues": len(problems),
    }
    print(json.dumps(summary, indent=2))
    return summary


if __name__ == "__main__":
    build()
