# Bộ công cụ Học Bá (dành cho Claude ở chat mới)

Thư mục này giúp chat mới làm tiếp ngay, không phải dựng lại từ đầu.

| File | Dùng để |
|---|---|
| `gen3.py` | Tạo lịch học (`data/schedule.json`) + dữ liệu trang lộ trình (`tools/D.json`). Muốn dời lịch: **chỉ sửa dict `P`** rồi chạy lại. |
| `check.py` | Kiểm tra trước khi đưa lên: không ngày nào vượt giờ, đủ bài, không trùng id, 240 câu đủ 3 đáp án + công thức. |
| `build_patch.py` | Đóng gói `hocba_patch.zip` từ thư mục làm việc. |
| `smoke_test.js` | Mở app trên máy ở một ngày giả lập, bấm mọi nút "Bắt đầu", báo lỗi. |
| `lo-trinh.html` | Mã nguồn trang lộ trình (artifact https://claude.ai/artifact/RHtaTq5e7ASbr1Qf5RZhQ5). |
| `workbook_240.json` | 240 câu gốc trong sách của cô (Unit, số câu, 3 đáp án, đáp án theo file của cô). |

## Quy trình dời lịch (nhanh, ít token)

1. Lấy file trong repo: `git clone https://github.com/mkhanhh/hocba` (nếu bị chặn, xin quyền truy cập repo `mkhanhh/hocba` cho phiên này).
2. Giải nén: `mkdir work && cd work && unzip -o ../hocba_app.zip && unzip -o ../hocba_patch.zip && cd ..`
3. Sửa dict `P` trong `tools/gen3.py`, chỉ sửa những ngày cần đổi:
   - `E(n)` học mới bộ n · `RL(n)` dò lại đến 100% · `RL(n, why=V2)` ôn vòng 2 · `SW(...)` ôn nhanh 240 câu / bài ôn của cô · `REC` nhắc lại.
   - Ngày bận cả ngày: đặt `P["ngày"] = []` (hoặc chỉ `[REC]`), rồi chuyển việc sang ngày còn trống giờ.
   - Giữ quy tắc: ngày 4 tiếng xếp khoảng 2–3,5 tiếng; mỗi ngày Nhắc lại → dò lại bài hôm trước → bài mới; xong 240 câu càng sớm càng tốt.
4. Chạy: `python3 tools/gen3.py work` rồi `python3 tools/check.py work` (phải ra "OK").
5. (Nếu đổi code) chạy app trên máy với `HOCBA_FAKE_NOW` và `node tools/smoke_test.js`, chỉ thử những ngày bị đổi.
6. Đóng gói: `python3 tools/build_patch.py work hocba_patch.zip`.
7. Đưa lên: mở https://github.com/mkhanhh/hocba/upload/main, tải `hocba_patch.zip`, commit. App **tự nạp bản mới** sau khoảng 30 giây, không cần Reboot.
8. Cập nhật trang lộ trình: thay dòng `const D=[...]` trong `tools/lo-trinh.html` bằng nội dung `tools/D.json`, rồi đăng lại vào artifact cũ (đọc artifact trước, đăng với `url` của nó). Nhớ đưa `lo-trinh.html` mới lên lại thư mục `tools/`.
9. Kiểm tra app thật 1 lần (ngày bị đổi hiện đúng việc), báo ngắn gọn cho Khánh.

## Những điều KHÔNG được làm

- Không đổi `RESET_ID` trong `hb/storage.py` (đổi là xóa tiến độ).
- Không đổi `id_n` của những việc đã làm xong ở các ngày đã qua.
- Không đổi đáp án 240 câu: đã khớp 100% với file đáp án của cô.
