"""Đóng gói hocba_patch.zip từ thư mục làm việc (app_main.py, hb/, data/). Cách dùng: python3 tools/build_patch.py work"""
import os, sys, zipfile
src = sys.argv[1] if len(sys.argv) > 1 else "work"
out = sys.argv[2] if len(sys.argv) > 2 else "hocba_patch.zip"
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    for top in ("app_main.py", "hb", "data"):
        p = os.path.join(src, top)
        if os.path.isfile(p):
            z.write(p, top); continue
        for root, dirs, files in os.walk(p):
            dirs[:] = [d for d in dirs if d != "__pycache__"]
            for f in files:
                full = os.path.join(root, f)
                z.write(full, os.path.relpath(full, src))
print("đã tạo", out, os.path.getsize(out) // 1024, "KB")
