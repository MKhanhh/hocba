"""Lịch v3 (từ 14/11): chỉ học tài liệu của cô (240 câu Unit 1–6, biến đổi câu, điền từ, bài đọc) + luyện đọc + 2 thi thử.
Sinh <EX>/data/schedule.json + tools/D.json.
Cách dùng: python3 tools/gen3.py work   (sửa lịch: chỉ sửa dict P bên dưới rồi chạy lại)"""
import json, os, random, sys
from datetime import date, timedelta

# Thư mục đã giải nén app (hocba_app.zip rồi chép đè hocba_patch.zip): chứa app_main.py, hb/, data/
EX = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("HOCBA_WORK", "work")
OUT_D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "D.json")   # dữ liệu cho trang lộ trình
IDX = {x["num"]: x for x in json.load(open(f"{EX}/data/exams/index.json"))}
cur = json.load(open(f"{EX}/data/schedule.json"))
keep = {x["date"]: x for x in cur if x["date"] in ("2026-10-18", "2026-10-30")}
WD = ["T2", "T3", "T4", "T5", "T6", "T7", "CN"]
WDL = ["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7", "Chủ nhật"]
SLOT = {0: ("Tối", 90), 1: ("Sáng", 120), 2: ("Chiều hoặc tối", 240), 3: ("Sáng và chiều", 240),
        4: ("Cả ngày", 240), 5: ("Chiều và tối", 240), 6: ("Chiều và tối", 240)}
FULL = {"2026-11-17", "2026-11-23", "2026-11-24"}
TRIP = {"2026-11-20", "2026-11-21", "2026-11-22"}
NOTE = {"2026-11-14": "Bận · tối học khoảng 1 tiếng", "2026-11-15": "Học bù ở trường · tối học khoảng 1 tiếng 30", "2026-11-17": "Trường cho nghỉ · chia 3 buổi",
        "2026-11-19": "Học sáng và chiều · tối lên xe đi Đà Lạt", "2026-11-20": "Đi Đà Lạt", "2026-11-21": "Đi Đà Lạt",
        "2026-11-22": "Tối về tới nhà", "2026-11-23": "Trường cho nghỉ · chia 3 buổi · bắt đầu ôn vòng 2",
        "2026-11-24": "Trường cho nghỉ · chia 3 buổi", "2026-11-25": "Thi thử 1", "2026-11-28": "Thi thử 4 như thi thật",
        "2026-11-29": "Ôn trọn bài của cô", "2026-11-30": "Tối chỉ nhắc lại · ngủ trước 23 giờ"}
AIH = "làm theo 6 bước"
MIN = {}            # phút học mới mỗi bộ
for n in range(30, 42): MIN[n] = 40
MIN.update({24: 35, 25: 35, 26: 25, 27: 35, 20: 25, 21: 25, 22: 15, 23: 15})
for n in range(42, 57): MIN[n] = 15

def nm(n): return IDX[n]["name"]
def E(n, part="1-50", m=None, how=""):
    if n == 28:
        q = 25 if part == "1-25" else 11
        t = f"Biến đổi câu của cô · câu {'1–25' if part == '1-25' else '26–36'} ({AIH})"
        return ({"type": "exam", "ref": 28, "mode": "new", "part": part, "title": t, "minutes": 60 if part == "1-25" else 30}, "d", None, q)
    q = IDX[n]["count"]
    if n in (16, 19):
        t = f"{nm(n)} · làm liền 60 phút như thi thật, rồi đọc giải thích câu sai"
        return ({"type": "exam", "ref": n, "mode": "new", "part": "1-50", "title": t, "minutes": 110}, "d", None, q)
    kind = "Luyện đọc" if n >= 42 else ""
    t = f"{nm(n)} ({AIH})" if n < 42 else f"{nm(n)} (đọc kỹ, gạch chân chỗ có đáp án)"
    return ({"type": "exam", "ref": n, "mode": "new", "part": part, "title": t, "minutes": m or MIN[n]}, "d", None, q)
def RL(n, part="1-50", m=None, why="dò lại bài hôm trước"):
    if n == 28:
        lab = f"Biến đổi câu của cô · câu {'1–25' if part == '1-25' else '26–36' if part == '26-50' else '1–36'}"
        cnt = 25 if part == "1-25" else 11 if part == "26-50" else 36
    else:
        lab, cnt = nm(n), IDX[n]["count"]
    mm = m or max(5, int(round(cnt * 0.55 / 5.0) * 5))
    return ({"type": "relearn", "ref": n, "part": part, "title": f"{why.capitalize()}: {lab} · làm đến khi đúng 100% (đáp án đảo)", "minutes": mm}, "o", None, 0)
def SW(ref, t, m):
    return ({"type": "recall_teacher", "ref": ref, "title": t, "minutes": m}, "s", None, 0)
def SELF(m, t, kind="o"):
    return ({"type": "self", "title": t, "minutes": m}, kind, None, 0)
REC = "RECALL"
U = lambda u, h: 30 + (u - 1) * 2 + h      # Unit u, nửa h (0: câu 1–20, 1: câu 21–40)
V2 = "ôn vòng 2"
P = {
"2026-11-14": [E(U(1, 0)), E(22)],
"2026-11-15": [REC, RL(U(1, 0)), RL(22), E(U(1, 1))],
"2026-11-16": [REC, RL(U(1, 1)), E(U(2, 0)), E(23)],
"2026-11-17": [REC, RL(U(2, 0)), RL(23), E(U(2, 1)), E(U(3, 0)), E(U(3, 1)), E(U(4, 0)), E(28, "1-25"), E(20)],
"2026-11-18": [REC, RL(U(2, 1)), RL(U(3, 0)), RL(U(3, 1)), RL(U(4, 0)), RL(28, "1-25"), RL(20), E(U(4, 1)), E(U(5, 0)), E(24)],
"2026-11-19": [REC, RL(U(4, 1)), RL(U(5, 0)), RL(24), E(U(5, 1)), E(U(6, 0)), E(28, "26-50"),
               SELF(5, "Mở app trên điện thoại, đăng nhập sẵn để nhắc lại trên xe")],
"2026-11-20": [REC], "2026-11-21": [REC], "2026-11-22": [REC],
"2026-11-23": [REC, RL(U(5, 1)), RL(U(6, 0)), RL(28, "26-50"), E(U(6, 1)), E(25), E(26), E(21), RL(U(1, 0), why=V2), RL(U(1, 1), why=V2), E(42), E(43)],
"2026-11-24": [REC, SW(None, "Ôn 240 câu của cô lượt 1 · làm câu chưa thuộc trước (đảo đáp án) · chia 2–3 lần", 60),
               RL(U(6, 1)), RL(25), RL(26), RL(21), E(27), RL(U(2, 0), why=V2), RL(U(2, 1), why=V2), RL(28, "1-50", why=V2), E(44), E(45)],
"2026-11-25": [REC, RL(27), E(16), E(46)],
"2026-11-26": [REC, RL(U(3, 0), why=V2), RL(U(3, 1), why=V2), RL(U(4, 0), why=V2), RL(U(4, 1), why=V2), RL(24, why=V2), RL(25, why=V2), E(47), E(48), E(51)],
"2026-11-27": [REC, RL(U(5, 0), why=V2), RL(U(5, 1), why=V2), RL(U(6, 0), why=V2), RL(U(6, 1), why=V2), RL(26, why=V2), RL(27, why=V2), RL(28, "1-50", why="ôn vòng 3"), E(49)],
"2026-11-28": [REC, E(19), E(50)],
"2026-11-29": [REC, SW("extra", "Ôn trọn bài ôn của cô (biến đổi câu, điền từ, bài đọc · đảo đáp án)", 40),
               SW(None, "Ôn 240 câu của cô lượt 2 · chỉ làm câu CHƯA THUỘC (đảo đáp án)", 55)],
"2026-11-30": [REC, RL(28, "1-50", why="ôn nhẹ trước ngày thi")],
}

GAPS = [1, 3, 6, 12, 20]; KG = [1, 2, 4]
def sim(seed):
    rnd = random.Random(seed); load = {}; items = []
    d = date(2026, 11, 14)
    while d <= date(2026, 11, 30):
        iso = d.isoformat()
        todo = [it for it in items if it["due"] <= iso]
        if iso in TRIP: todo = todo[:40]
        load[iso] = len(todo)
        def upd(it, ok):
            it["box"] = min(it["box"] + 1, 4) if ok else 0
            it["due"] = (d + timedelta(days=GAPS[it["box"]])).isoformat()
            if it["key"]:
                it["st"] = min(3, it["st"] + 1) if ok else 0
                if it["st"] < 3:
                    it["due"] = min(d + timedelta(days=KG[it["st"]] if ok else 1), max(d + timedelta(days=1), date(2026, 11, 29))).isoformat()
        for it in todo: upd(it, rnd.random() < (0.7 if it["box"] <= 0 else 0.85))
        for x in P.get(iso, []):
            if x != REC and x[0]["type"] == "exam" and x[0]["ref"] not in (16, 19):
                key = 30 <= x[0]["ref"] <= 41 or x[0]["ref"] == 28
                for _ in range(x[3]):
                    it = {"box": 0, "st": 0, "key": key, "ref": x[0]["ref"]}
                    upd(it, rnd.random() < 0.6); items.append(it)
        d += timedelta(days=1)
    return load, items
R = [sim(s) for s in range(20)]
LOAD = {k: sum(r[0][k] for r in R) / len(R) for k in R[0][0]}

def dlabel(d): return f"{WDL[d.weekday()]}, {d.day}/{d.month}"
out = [dict(keep["2026-10-18"], tasks=[], new_words=[]), dict(keep["2026-10-30"], tasks=[], new_words=[], slot="Đã qua", budget=0)]
html = []
d = date(2026, 10, 31)
while d <= date(2026, 12, 1):
    iso = d.isoformat()
    slot, bud = SLOT[d.weekday()]
    if iso in FULL: slot, bud = "Cả ngày (trường cho nghỉ)", 360
    if iso in TRIP: slot, bud = "Đi Đà Lạt", 30
    if iso == "2026-11-15": slot, bud = "Tối (ban ngày học bù)", 90
    day = {"date": iso, "wd": WD[d.weekday()], "label": dlabel(d), "slot": slot, "budget": bud, "tasks": [], "new_words": []}
    if iso < "2026-11-14":
        day.update(slot="Đã qua", budget=0)
    elif iso == "2026-12-01":
        day.update(slot="Sáng ôn nhẹ · chiều thi", budget=120)
        day["tasks"] = [{"type": "recall", "title": "Sáng: nhắc lại câu đến hạn, tối đa 30 phút (không học câu mới)", "minutes": 30, "id_n": 200},
                        {"type": "self", "title": "Sáng: đọc lại ghi chú các câu còn hay sai, viết ra giấy điều đang lo 10 phút", "minutes": 25, "id_n": 201},
                        {"type": "exam_day", "title": "CHIỀU THI. Nghỉ ngơi, ăn trưa no, đến sớm. Làm câu dễ trước, không bỏ trống câu nào.", "minutes": 5, "id_n": 202}]
        html.append([iso, 120, [[t["minutes"], "s" if t["type"] == "recall" else "o", t["title"]] for t in day["tasks"]], "Sáng ôn nhẹ · chiều thi"])
    else:
        rows = []
        seq = list(P[iso])
        if any(x != REC and x[0]["type"] == "exam" for x in seq):
            k = next((i for i, x in enumerate(seq) if x != REC and x[0]["type"] == "exam"), 0)
            seq.insert(k, "GUIDE")
        for i, it in enumerate(seq):
            if it == REC:
                n = int(round(LOAD[iso])); m = max(10, int(round(n * 0.35 / 5.0) * 5))
                if iso in TRIP:
                    task = {"type": "recall", "title": f"Nhắc lại trên điện thoại ~20 phút nếu tiện (không bắt buộc). Khoảng {n} câu đến hạn, làm được bao nhiêu thì làm.", "minutes": 20}
                elif n == 0:
                    task = {"type": "recall", "title": "Nhắc lại câu đến hạn (nếu có)", "minutes": 10}
                else:
                    task = {"type": "recall", "title": f"Nhắc lại câu đến hạn (khoảng {n} câu, đáp án đã đảo) · chia nhỏ trong ngày được", "minutes": m}
                kind = "s"
            elif it == "GUIDE":
                task = {"type": "self", "guide": True, "title": "Đọc 6 bước làm 1 câu trước khi học bài mới (1 phút)", "minutes": 2}; kind = "o"
            else:
                task, kind, _, _ = it; task = dict(task)
            task["id_n"] = 200 + i
            day["tasks"].append(task)
            rows.append([task["minutes"], kind, task["title"]])
        tot = sum(t["minutes"] for t in day["tasks"])
        if tot > bud: print("VUOT", iso, tot, bud)
        html.append([iso, bud, rows] + ([NOTE[iso]] if iso in NOTE else []))
    out.append(day)
    d += timedelta(days=1)
json.dump(out, open(f"{EX}/data/schedule.json", "w"), ensure_ascii=False, indent=1)
json.dump([h for h in html if h[0] >= "2026-11-14"], open(OUT_D, "w"), ensure_ascii=False)
for x in out:
    if x["date"] >= "2026-11-14":
        m = sum(t["minutes"] for t in x["tasks"]); rec = sum(t["minutes"] for t in x["tasks"] if t["type"] == "recall")
        print(x["date"], x["wd"], x["budget"], "tổng", m, "nhắc lại", rec, f"(~{int(LOAD.get(x['date'],0))} câu)")
# ước tính thuộc
st = [sum(1 for it in r[1] if it["key"] and it["st"] >= 3) / max(1, sum(1 for it in r[1] if it["key"])) for r in R]
print("THUỘC (đúng 3 ngày) ước tính: %.0f%%" % (100 * sum(st) / len(st)))
