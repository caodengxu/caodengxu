from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional


CATEGORY_CAMERA = "camera"
CATEGORY_SCREENSHOT = "screenshot"
CATEGORY_DOWNLOAD = "download"
CATEGORY_APP_MEDIA = "app_media"
CATEGORY_APP_CACHE = "app_cache"
CATEGORY_UNKNOWN = "unknown"


@dataclass
class PathHints:
    category: str
    package_name: Optional[str]


def infer_package_name(path: Path) -> Optional[str]:
    parts = [part.lower() for part in path.parts]
    for anchor in ("android", "media", "data"):
        if anchor in parts:
            index = parts.index(anchor)
            if index + 1 < len(parts):
                candidate = parts[index + 1]
                if "." in candidate:
                    return candidate
    return None


def classify_path(path: Path) -> PathHints:
    parts = [part.lower() for part in path.parts]
    package_name = infer_package_name(path)

    if "dcim" in parts and "camera" in parts:
        return PathHints(category=CATEGORY_CAMERA, package_name=package_name)
    if "screenshots" in parts or "screen_shot" in parts:
        return PathHints(category=CATEGORY_SCREENSHOT, package_name=package_name)
    if "download" in parts:
        return PathHints(category=CATEGORY_DOWNLOAD, package_name=package_name)
    if "android" in parts and "media" in parts:
        return PathHints(category=CATEGORY_APP_MEDIA, package_name=package_name)
    if "android" in parts and "data" in parts and "cache" in parts:
        return PathHints(category=CATEGORY_APP_CACHE, package_name=package_name)

    return PathHints(category=CATEGORY_UNKNOWN, package_name=package_name)
