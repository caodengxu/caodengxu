from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from app.core.audit_log import AuditLogger


@dataclass
class CasePaths:
    root: Path
    database: Path
    evidence_dir: Path
    reports_dir: Path
    derived_dir: Path
    logs_dir: Path


@dataclass
class CaseContext:
    paths: CasePaths
    operator: str
    audit_logger: AuditLogger


class CaseManager:
    def __init__(self, root: Path) -> None:
        self.root = root

    def create(self, operator: str) -> CaseContext:
        paths = self._ensure_paths()
        audit_logger = AuditLogger(paths.logs_dir / "audit.jsonl")
        audit_logger.log("case_created", {"operator": operator, "root": str(paths.root)})
        return CaseContext(paths=paths, operator=operator, audit_logger=audit_logger)

    def open(self, operator: str) -> CaseContext:
        paths = self._ensure_paths()
        audit_logger = AuditLogger(paths.logs_dir / "audit.jsonl")
        audit_logger.log("case_opened", {"operator": operator, "root": str(paths.root)})
        return CaseContext(paths=paths, operator=operator, audit_logger=audit_logger)

    def _ensure_paths(self) -> CasePaths:
        root = self.root
        root.mkdir(parents=True, exist_ok=True)
        evidence_dir = root / "evidence"
        reports_dir = root / "reports"
        derived_dir = root / "derived"
        logs_dir = root / "logs"
        for path in (evidence_dir, reports_dir, derived_dir, logs_dir):
            path.mkdir(parents=True, exist_ok=True)
        database = root / "case.db"
        return CasePaths(
            root=root,
            database=database,
            evidence_dir=evidence_dir,
            reports_dir=reports_dir,
            derived_dir=derived_dir,
            logs_dir=logs_dir,
        )


@dataclass
class EvidenceRecord:
    evidence_id: int
    source_path: Path
    note: Optional[str]
    operator: str
