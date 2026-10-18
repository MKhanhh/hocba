"""HỌC BÁ – file khởi động.

Toàn bộ app (code + 19 đề + từ vựng + bài học) nằm gọn trong hocba_app.zip.
Nếu có thêm hocba_patch.zip (bản sửa nhỏ) thì các file trong đó được chép ĐÈ lên bản gốc.
File này tự giải nén (chỉ lần đầu, hoặc khi một trong hai zip được thay bản mới) rồi chạy app.
"""
import hashlib
import runpy
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
BUNDLE = HERE / "hocba_app.zip"
PATCH = HERE / "hocba_patch.zip"      # không bắt buộc


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
    h = hashlib.sha256(BUNDLE.read_bytes())
    if PATCH.exists():
        h.update(PATCH.read_bytes())
    digest = h.hexdigest()[:16]
    mark = d / ".bundle"
    if not mark.exists() or mark.read_text() != digest:
        for name in ("hb", "data", "app_main.py"):      # xóa bản cũ (KHÔNG đụng file tiến độ)
            p = d / name
            if p.is_dir():
                shutil.rmtree(p, ignore_errors=True)
            elif p.exists():
                p.unlink()
        with zipfile.ZipFile(BUNDLE) as z:
            z.extractall(d)
        if PATCH.exists():
            with zipfile.ZipFile(PATCH) as z:
                z.extractall(d)
        mark.write_text(digest)
    return d


APP_DIR = _prepare()
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))
runpy.run_path(str(APP_DIR / "app_main.py"), run_name="__main__")
