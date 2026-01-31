from __future__ import annotations

import json
import mimetypes
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, Optional

from app.core.adapters.base_android import classify_path
from app.core.evidence_importer import compute_sha256, iter_image_files


@dataclass
class IndexStats:
    total: int


def _init_db(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            evidence_id INTEGER,
            rel_path TEXT,
            abs_path TEXT,
            file_name TEXT,
            ext TEXT,
            mime TEXT,
            size INTEGER,
            mtime TEXT,
            ctime TEXT,
            sha256 TEXT,
            package_name TEXT,
            app_name TEXT,
            category TEXT,
            origin_guess TEXT,
            meta_json TEXT
        );
        """
    )
    conn.execute("CREATE INDEX IF NOT EXISTS idx_images_sha256 ON images(sha256);")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_images_category ON images(category);")


def _load_app_map(path: Path) -> Dict[str, str]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def iter_records(
    evidence_id: int,
    source: Path,
    app_map: Dict[str, str],
    meta_provider: Optional[callable] = None,
) -> Iterable[dict]:
    for file_path in iter_image_files(source):
        rel_path = file_path.relative_to(source)
        hints = classify_path(file_path)
        mime, _ = mimetypes.guess_type(file_path.name)
        stat = file_path.stat()
        meta = meta_provider(file_path) if meta_provider else {}
        yield {
            "evidence_id": evidence_id,
            "rel_path": str(rel_path),
            "abs_path": str(file_path),
            "file_name": file_path.name,
            "ext": file_path.suffix.lower(),
            "mime": mime or "application/octet-stream",
            "size": stat.st_size,
            "mtime": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "ctime": datetime.fromtimestamp(stat.st_ctime).isoformat(),
            "sha256": compute_sha256(file_path),
            "package_name": hints.package_name,
            "app_name": app_map.get(hints.package_name) if hints.package_name else None,
            "category": hints.category,
            "origin_guess": None,
            "meta_json": json.dumps(meta, ensure_ascii=False),
        }


def index_images(
    db_path: Path,
    evidence_id: int,
    source: Path,
    app_map_path: Path,
    meta_provider: Optional[callable] = None,
) -> IndexStats:
    conn = sqlite3.connect(db_path)
    _init_db(conn)
    app_map = _load_app_map(app_map_path)

    total = 0
    for record in iter_records(evidence_id, source, app_map, meta_provider=meta_provider):
        conn.execute(
            """
            INSERT INTO images (
                evidence_id, rel_path, abs_path, file_name, ext, mime, size,
                mtime, ctime, sha256, package_name, app_name, category,
                origin_guess, meta_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """,
            (
                record["evidence_id"],
                record["rel_path"],
                record["abs_path"],
                record["file_name"],
                record["ext"],
                record["mime"],
                record["size"],
                record["mtime"],
                record["ctime"],
                record["sha256"],
                record["package_name"],
                record["app_name"],
                record["category"],
                record["origin_guess"],
                record["meta_json"],
            ),
        )
        total += 1

    conn.commit()
    conn.close()
    return IndexStats(total=total)
