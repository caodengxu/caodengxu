# 手机图片取证与溯源分析系统（骨架）

本仓库提供一个从零搭建的手机图片取证与溯源分析系统骨架，实现了：

- 案件/证据管理与审计日志
- 证据导入 + SHA-256 清单
- 全量图片扫描 + SQLite 索引
- 路径语义分类 + 包名推断
- 单图溯源分析（小米 / ChatGPT / 未知）与依据展示
- 简版 HTML 报告导出

> 说明：图像像素级取证（pHash/缩略图对比）留出接口，可后续补齐。

## 快速开始（CLI 示例）

```bash
python -m app.core.cli \
  --case /path/to/case \
  --evidence /path/to/evidence_dir \
  --operator "analyst" \
  --note "offline evidence"
```

## 目录结构

```
app/
  core/
    cli.py
    case_manager.py
    evidence_importer.py
    indexer.py
    audit_log.py
    report_service.py
    adapters/
      base_android.py
    image_forensics/
      metadata.py
      provenance.py
      phash.py
      thumbnail.py
  gui/
    main_window.py
    image_list_widget.py
    provenance_dialog.py
    case_dialog.py
app/resources/
  app_name_map.json
```

