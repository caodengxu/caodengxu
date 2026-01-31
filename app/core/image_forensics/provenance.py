from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional


XIAOMI_KEYWORDS = ("xiaomi", "redmi", "poco", "miui")
CHATGPT_KEYWORDS = ("openai", "chatgpt", "dall-e", "dalle")


@dataclass
class ProvenanceResult:
    origin: str
    evidence: List[str]


def _collect_strings(meta: Dict[str, object]) -> List[str]:
    values: List[str] = []
    exif = meta.get("exif", {}) if isinstance(meta.get("exif"), dict) else {}
    for key in ("Make", "Model", "Software", "DateTime", "DateTimeOriginal"):
        value = exif.get(key)
        if isinstance(value, str):
            values.append(value)
    xmp = meta.get("xmp")
    if isinstance(xmp, str):
        values.append(xmp)
    return values


def infer_origin(meta: Dict[str, object], package_name: Optional[str]) -> ProvenanceResult:
    evidence: List[str] = []
    candidates = [value.lower() for value in _collect_strings(meta)]

    if package_name:
        candidates.append(package_name.lower())

    for value in candidates:
        if any(keyword in value for keyword in XIAOMI_KEYWORDS):
            evidence.append(f"命中小米关键词: {value}")

    if evidence:
        return ProvenanceResult(origin="xiaomi", evidence=evidence)

    chatgpt_hits = []
    for value in candidates:
        if any(keyword in value for keyword in CHATGPT_KEYWORDS):
            chatgpt_hits.append(f"命中ChatGPT关键词: {value}")
    if chatgpt_hits:
        return ProvenanceResult(origin="chatgpt", evidence=chatgpt_hits)

    return ProvenanceResult(origin="unknown", evidence=["未命中已知关键词"])
