from __future__ import annotations

import argparse
from pathlib import Path

from app.core.case_manager import CaseManager
from app.core.evidence_importer import create_manifest
from app.core.image_forensics.metadata import extract_metadata
from app.core.image_forensics.provenance import infer_origin
from app.core.indexer import index_images
from app.core.report_service import export_html_report


def main() -> None:
    parser = argparse.ArgumentParser(description="手机图片取证平台 CLI")
    parser.add_argument("--case", required=True, type=Path)
    parser.add_argument("--evidence", required=True, type=Path)
    parser.add_argument("--operator", required=True)
    parser.add_argument("--note", default="")
    args = parser.parse_args()

    case_manager = CaseManager(args.case)
    context = case_manager.create(operator=args.operator)

    context.audit_logger.log(
        "evidence_registered",
        {
            "source": str(args.evidence),
            "operator": args.operator,
            "note": args.note,
        },
    )

    manifest = create_manifest(args.evidence, context.paths.derived_dir)
    context.audit_logger.log(
        "manifest_created",
        {"manifest_csv": str(manifest.manifest_csv), "total": manifest.total_files},
    )

    stats = index_images(
        context.paths.database,
        evidence_id=1,
        source=args.evidence,
        app_map_path=Path("app/resources/app_name_map.json"),
        meta_provider=extract_metadata,
    )

    context.audit_logger.log("index_completed", {"total": stats.total})

    provenance_samples = []
    if stats.total:
        meta = extract_metadata(next(args.evidence.rglob("*")))
        provenance = infer_origin(meta, package_name=None)
        provenance_samples.append(
            {"origin": provenance.origin, "evidence": provenance.evidence}
        )

    report = export_html_report(
        context.paths.reports_dir,
        {
            "case": str(context.paths.root),
            "evidence": str(args.evidence),
            "images_indexed": stats.total,
            "provenance_samples": provenance_samples,
        },
    )

    context.audit_logger.log("report_exported", {"report": str(report.report_path)})


if __name__ == "__main__":
    main()
