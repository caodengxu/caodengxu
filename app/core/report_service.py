from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict


@dataclass
class ReportResult:
    report_path: Path


def export_html_report(output_dir: Path, summary: Dict[str, object]) -> ReportResult:
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    report_path = output_dir / f"report_{timestamp}.html"

    body = f"""
    <html>
      <head>
        <meta charset="utf-8" />
        <title>手机图片取证报告</title>
      </head>
      <body>
        <h1>手机图片取证报告</h1>
        <p>生成时间：{datetime.utcnow().isoformat()}Z</p>
        <pre>{json.dumps(summary, ensure_ascii=False, indent=2)}</pre>
      </body>
    </html>
    """
    report_path.write_text(body, encoding="utf-8")
    return ReportResult(report_path=report_path)
