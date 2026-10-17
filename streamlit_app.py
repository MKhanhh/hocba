"""HỌC BÁ – file khởi động.

Toàn bộ app (code + 19 đề + từ vựng + bài học) nằm gọn trong hocba_app.zip.
File này tự giải nén zip (chỉ lần đầu, hoặc khi zip được thay bản mới) rồi chạy app.
Nhờ vậy khi đưa lên GitHub chỉ cần tải vài file, không phải tạo từng thư mục.
"""
import hashlib
import runpy
import sys
import tempfile
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
BUNDLE = HERE / "hocba_app.zip"


def _target() -> Path:
    for base in (HERE, Path(tempfile.gettempdir())):
        d = base / "_hocba_app"
        try:
            d.mkdir(exist_ok=True)
            (d / ".w").write_text("ok")
            return d
        except OSError:
            continue
    raise RuntimeError("Không có chỗ để giải nén app.")


def _prepare() -> Path:
    d = _target()
    digest = hashlib.sha256(BUNDLE.read_bytes()).hexdigest()[:16]
    mark = d / ".bundle"
    if not mark.exists() or mark.read_text() != digest:
        with zipfile.ZipFile(BUNDLE) as z:
            z.extractall(d)
        mark.write_text(digest)
    return d


APP_DIR = _prepare()
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))
runpy.run_path(str(APP_DIR / "app_main.py"), run_name="__main__")
