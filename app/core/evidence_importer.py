from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from datetime import datetime
from hashlib import sha256
from pathlib import Path
from typing import Iterable, List


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".heic"}


@dataclass
class EvidenceImportResult:
    manifest_csv: Path
    manifest_json: Path
    total_files: int


def iter_image_files(source: Path) -> Iterable[Path]:
    for path in source.rglob("*"):
        if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS:
            yield path


def compute_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def create_manifest(source: Path, output_dir: Path) -> EvidenceImportResult:
    output_dir.mkdir(parents=True, exist_ok=True)
    rows: List[dict] = []
    for file_path in iter_image_files(source):
        rows.append(
            {
                "rel_path": str(file_path.relative_to(source)),
                "sha256": compute_sha256(file_path),
                "size": file_path.stat().st_size,
            }
        )

    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    csv_path = output_dir / f"hash_manifest_{timestamp}.csv"
    json_path = output_dir / f"hash_manifest_{timestamp}.json"

    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["rel_path", "sha256", "size"])
        writer.writeheader()
        writer.writerows(rows)

    with json_path.open("w", encoding="utf-8") as handle:
        json.dump(rows, handle, ensure_ascii=False, indent=2)

    return EvidenceImportResult(
        manifest_csv=csv_path,
        manifest_json=json_path,
        total_files=len(rows),
    )
