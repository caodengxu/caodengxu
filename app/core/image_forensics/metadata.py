from __future__ import annotations

import struct
from pathlib import Path
from typing import Dict, Optional


JPEG_SOI = b"\xFF\xD8"
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
WEBP_SIGNATURE = b"RIFF"
GIF_SIGNATURE = b"GIF"
BMP_SIGNATURE = b"BM"


def detect_format(data: bytes) -> str:
    if data.startswith(JPEG_SOI):
        return "jpeg"
    if data.startswith(PNG_SIGNATURE):
        return "png"
    if data.startswith(WEBP_SIGNATURE) and data[8:12] == b"WEBP":
        return "webp"
    if data.startswith(GIF_SIGNATURE):
        return "gif"
    if data.startswith(BMP_SIGNATURE):
        return "bmp"
    return "unknown"


def _parse_exif_ifd(data: bytes, base: int, offset: int, endian: str) -> Dict[str, str]:
    result: Dict[str, str] = {}
    tag_map = {
        0x010F: "Make",
        0x0110: "Model",
        0x0131: "Software",
        0x0132: "DateTime",
        0x9003: "DateTimeOriginal",
    }
    count = struct.unpack_from(f"{endian}H", data, base + offset)[0]
    cursor = base + offset + 2
    for _ in range(count):
        tag, type_id, count_value, value_or_offset = struct.unpack_from(
            f"{endian}HHII", data, cursor
        )
        cursor += 12
        if tag not in tag_map:
            continue
        if type_id == 2:  # ASCII
            size = count_value
            if size <= 4:
                raw = struct.pack(f"{endian}I", value_or_offset)[:size]
            else:
                raw = data[base + value_or_offset : base + value_or_offset + size]
            value = raw.rstrip(b"\x00").decode("utf-8", errors="replace")
            result[tag_map[tag]] = value
    return result


def parse_exif_from_jpeg(data: bytes) -> Dict[str, str]:
    offset = 2
    while offset < len(data) - 4:
        if data[offset] != 0xFF:
            offset += 1
            continue
        marker = data[offset : offset + 2]
        if marker == b"\xFF\xE1":
            length = struct.unpack_from(">H", data, offset + 2)[0]
            segment = data[offset + 4 : offset + 2 + length]
            if segment.startswith(b"Exif\x00\x00"):
                tiff = segment[6:]
                endian = "<" if tiff[:2] == b"II" else ">"
                if struct.unpack_from(f"{endian}H", tiff, 2)[0] != 42:
                    return {}
                ifd_offset = struct.unpack_from(f"{endian}I", tiff, 4)[0]
                return _parse_exif_ifd(tiff, 0, ifd_offset, endian)
            return {}
        if marker in (b"\xFF\xD9", b"\xFF\xDA"):
            break
        length = struct.unpack_from(">H", data, offset + 2)[0]
        offset += 2 + length
    return {}


def extract_xmp(data: bytes) -> Optional[str]:
    marker = b"<x:xmpmeta"
    end_marker = b"</x:xmpmeta>"
    start = data.find(marker)
    if start == -1:
        return None
    end = data.find(end_marker, start)
    if end == -1:
        return None
    payload = data[start : end + len(end_marker)]
    return payload.decode("utf-8", errors="replace")


def extract_metadata(path: Path) -> Dict[str, object]:
    data = path.read_bytes()
    fmt = detect_format(data)
    exif = {}
    if fmt == "jpeg":
        exif = parse_exif_from_jpeg(data)
    xmp = extract_xmp(data)
    return {
        "file_header": {"format": fmt, "magic": data[:12].hex()},
        "exif": exif,
        "xmp": xmp,
    }
