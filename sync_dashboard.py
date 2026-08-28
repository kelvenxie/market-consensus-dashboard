#!/usr/bin/env python3
"""驗證正式儀表板後，同步成 GitHub Pages 的 index.html。"""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import tempfile
from html.parser import HTMLParser
from pathlib import Path


PUBLISH_DIR = Path(__file__).resolve().parent
PROJECT_DIR = PUBLISH_DIR.parent
DEFAULT_SOURCE = PROJECT_DIR / "報告" / "市場共識儀表板.html"
TARGET = PUBLISH_DIR / "index.html"
MIN_BYTES = 10_000


class DashboardParser(HTMLParser):
    """只做結構解析；內容事實仍由正式管線的閘門負責。"""


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def validate(raw: bytes, source: Path) -> str:
    """檢查編碼、HTML 結構與不應公開的明顯字串。"""
    if len(raw) < MIN_BYTES:
        raise ValueError(f"HTML 過小：{len(raw):,} bytes，最低要求 {MIN_BYTES:,} bytes")

    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("HTML 不是有效 UTF-8") from exc

    lowered = text.lower()
    if "<html" not in lowered or "</html>" not in lowered:
        raise ValueError("缺少完整的 <html> 標籤")

    parser = DashboardParser()
    parser.feed(text)
    parser.close()

    blocked_patterns = {
        "本機使用者路徑": r"(?:/Users/|file://)",
        "Authorization 憑證": r"(?i)authorization\s*[:=]\s*['\"][^'\"]+",
        "Bearer Token": r"(?i)bearer\s+[a-z0-9._-]{20,}",
        "API Key 指派": r"(?i)api[_-]?key\s*[:=]\s*['\"][^'\"]+",
    }
    for label, pattern in blocked_patterns.items():
        if re.search(pattern, text):
            raise ValueError(f"偵測到不應公開的內容：{label}")

    return text


def atomic_write(raw: bytes, target: Path) -> None:
    """同目錄寫入暫存檔後替換，避免中斷時留下半份 HTML。"""
    fd, temp_name = tempfile.mkstemp(prefix="index.", suffix=".tmp", dir=target.parent)
    temp_path = Path(temp_name)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(raw)
            handle.flush()
            os.fsync(handle.fileno())
        temp_path.replace(target)
    finally:
        temp_path.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="同步市場共識儀表板到 GitHub Pages 資料夾")
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE, help="正式 HTML 路徑")
    parser.add_argument("--check-only", action="store_true", help="只驗證，不更新 index.html")
    args = parser.parse_args()

    source = args.source.expanduser().resolve()
    if not source.is_file():
        print(f"❌ 找不到正式 HTML：{source}")
        return 2

    raw = source.read_bytes()
    try:
        validate(raw, source)
    except (ValueError, OSError) as exc:
        print(f"❌ HTML 驗證失敗：{exc}")
        return 1

    digest = sha256(raw)
    if args.check_only:
        print(f"✅ HTML 驗證通過：{len(raw):,} bytes｜SHA-256 {digest}")
        return 0

    if TARGET.exists() and TARGET.read_bytes() == raw:
        print(f"✅ index.html 已是最新版本：{len(raw):,} bytes｜SHA-256 {digest}")
        return 0

    atomic_write(raw, TARGET)
    print(f"✅ 已同步 index.html：{len(raw):,} bytes｜SHA-256 {digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

