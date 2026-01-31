from __future__ import annotations

from pathlib import Path
from typing import Optional


def compute_phash(path: Path) -> Optional[str]:
    raise NotImplementedError("pHash 需要引入图像解码库（如 Pillow）。")
