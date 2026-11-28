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
FULL = {"2026-11-23", "2026-11-24"}
TRIP = set()
CAP = {"2026-11-30": (280, 100, "Nhắc lại câu đến hạn tối đa 100 phút · làm câu Đề ôn sát đề và câu hay sai trước")}      # ngày bận: chỉ nhắc lại được khoảng chừng này câu
NOTE = {**{f"2026-11-{d}": "Bận · nghỉ" for d in range(14, 26)},
        "2026-11-26": "Đã học Unit 1 · Điền từ I và Unit 2 câu 1–20 dời sang Thứ 6",
        "2026-11-27": "Học ĐỀ ÔN SÁT ĐỀ trước · Unit 3 câu 21–40 + Đọc 2 dời sang Thứ 7",
        "2026-11-28": "Học được Unit 3 câu 21–40, Đọc 2, Unit 4 câu 1–20 · 9 bài còn lại dời sang Chủ nhật",
        "2026-11-29": "Học bù 9 bài của Thứ 7 + học xong hết · dậy 2h · 4 buổi: 2h–5h30, 7h–11h, 12h30–16h, 18h–21h · ngủ trưa 1 tiếng",
        "2026-11-30": "Chỉ 2 tiếng: nhắc lại + ôn nhanh đề ôn sát đề · ngủ trước 22 giờ"}
AIH = "làm theo 4 bước"
MIN = {}            # phút học mới mỗi bộ
for n in range(30, 42): MIN[n] = 35   # có mẹo "Thấy → chọn" nên nhanh hơn
MIN.update({24: 35, 25: 35, 26: 25, 27: 35, 20: 25, 21: 25, 22: 15, 23: 15})
MIN.update({57: 25, 58: 25, 59: 40, 60: 15, 61: 12, 62: 12})   # Đề ôn sát đề (cô gửi 26/11)
for n in range(42, 57): MIN[n] = 15

def nm(n): return IDX[n]["name"]
def E(n, part="1-50", m=None, how=""):
    if n == 28:
        q = 25 if part == "1-25" else 11
        t = f"Biến đổi câu của cô · câu {'1–25' if part == '1-25' else '26–36'} ({AIH})"
        # câu 1–25: 10 câu đã học trong Đề ôn sát đề · 3. Biến đổi câu (27/11) → chỉ còn 15 câu mới, 45 phút là đủ
        return ({"type": "exam", "ref": 28, "mode": "new", "part": part, "title": t, "minutes": 45 if part == "1-25" else 30}, "d", None, q)
    q = IDX[n]["count"]
    if n in (16, 19):
        t = f"{nm(n)} · làm liền 60 phút như thi thật, rồi đọc giải thích câu sai"
        return ({"type": "exam", "ref": n, "mode": "new", "part": "1-50", "title": t, "minutes": 110}, "d", None, q)
    kind = "Luyện đọc" if n >= 42 else ""
    t = f"{nm(n)} ({AIH})" if (n < 42 or n >= 57) else f"{nm(n)} (đọc kỹ, gạch chân chỗ có đáp án)"
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
SKIP = "SKIP"      # việc đã dời sang ngày khác: giữ chỗ để mã (id_n) các việc đã xong trong ngày không đổi
U = lambda u, h: 30 + (u - 1) * 2 + h      # Unit u, nửa h (0: câu 1–20, 1: câu 21–40)
V2 = "ôn vòng 2"
TV = "buổi tối dò lại bài buổi sáng"
BT = "dò lại bài buổi trước"
P = {
**{f"2026-11-{d}": [] for d in range(14, 26)},
"2026-11-26": [E(U(1, 0)), E(U(1, 1))],
# 27/11: chưa làm Unit 3 câu 21–40, Đọc 2 và dò lại tối Từ vựng → dời sang 28/11 (dò Từ vựng: đã có RL(57) sáng 28)
"2026-11-27": [REC, RL(U(1, 0)), RL(U(1, 1)), E(57), E(58), E(U(2, 0)), E(U(2, 1)), E(59), E(24), E(U(3, 0)), E(60), SKIP, SKIP,
               SKIP, RL(58, why=TV), RL(U(2, 0), why=TV), RL(U(2, 1), why=TV)],
# 28/11: còn 10 việc chưa làm → dời hết sang CN 29/11 (bạn dậy 2h, học 4 buổi ~11 tiếng). SKIP giữ mã các việc đã xong.
"2026-11-28": [REC, RL(57), RL(58), RL(U(2, 0)), RL(U(2, 1)), RL(59), RL(24), RL(U(3, 0)), RL(60), E(U(3, 1)), E(22),
               E(U(4, 0)), SKIP, SKIP, SKIP, SKIP, SKIP, SKIP, SKIP, SKIP, SKIP,
               RL(U(4, 0), why=TV), SKIP],
"2026-11-29": [REC,
               # Buổi 1 · 2h–5h30: dò lại bài hôm qua → Đề ôn sát đề (2 bài đọc) → Biến đổi câu → Unit 4, 5
               RL(U(3, 1)), RL(22), RL(U(4, 0)),
               E(61), E(62), E(28, "1-25"), E(U(4, 1)), E(U(5, 0)),
               # Buổi 2 · 7h–11h
               E(25), E(U(5, 1)), E(28, "26-50"), E(27), E(U(6, 0)), E(23),
               # Buổi 3 · 12h30–16h: dò lại bài buổi 1 trước, rồi học tiếp
               RL(61, why=BT), RL(62, why=BT), RL(28, "1-25", why=BT), RL(U(4, 1), why=BT), RL(U(5, 0), why=BT),
               E(26), E(U(6, 1)), E(21, m=20), E(20, m=20),
               # Buổi 4 · 18h–21h: dò lại bài buổi 2–3 + ôn nhanh cả Đề ôn sát đề
               RL(25, why=BT), RL(U(5, 1), why=BT), RL(28, "26-50", why=BT), RL(27, why=BT), RL(U(6, 0), why=BT), RL(U(6, 1), why=BT),
               SW("handout", "Tối: ôn nhanh cả Đề ôn sát đề của cô (đảo đáp án) · chỗ nào sai đọc lại mẹo", 30)],
"2026-11-30": [REC, SW("handout", "Ôn nhanh Đề ôn sát đề của cô lần cuối (đảo đáp án) · chỗ nào sai đọc lại mẹo", 20)],
}

GAPS = [1, 3, 6, 12, 20]; KG = [1, 2, 4]
def sim(seed):
    rnd = random.Random(seed); load = {}; items = []
    d = date(2026, 11, 14)
    while d <= date(2026, 11, 30):
        iso = d.isoformat()
        todo = [it for it in items if it["due"] <= iso]
        if iso in TRIP: todo = todo[:40]
        if iso in CAP: todo = todo[:CAP[iso][0]]
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
            if x not in (REC, SKIP) and x[0]["type"] == "exam" and x[0]["ref"] not in (16, 19):
                key = 30 <= x[0]["ref"] <= 41 or x[0]["ref"] == 28 or 57 <= x[0]["ref"] <= 62
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
    BUDO = {**{f"2026-11-{d}": ("Bận", 0) for d in range(14, 26)},
            "2026-11-26": ("2 giờ 15 – 5 giờ sáng · sau đó đi học", 150),
            "2026-11-27": ("10 giờ sáng – 9 giờ tối (đã trừ ăn, nghỉ, giải lao)", 400),
            "2026-11-28": ("7 giờ sáng – 9 giờ tối (đã trừ ăn, nghỉ, giải lao)", 460), "2026-11-29": ("2h–5h30 · 7h–11h · 12h30–16h · 18h–21h (đã trừ nghỉ giữa giờ)", 660),
            "2026-11-30": ("Rảnh 2 tiếng · chỉ ôn, không học bài mới", 120)}
    if iso in BUDO: slot, bud = BUDO[iso]
    day = {"date": iso, "wd": WD[d.weekday()], "label": dlabel(d), "slot": slot, "budget": bud, "tasks": [], "new_words": []}
    if iso < "2026-11-14":
        day.update(slot="Đã qua", budget=0)
    elif iso == "2026-12-01":
        day.update(slot="Sáng ôn nhẹ · chiều thi", budget=120)
        day["tasks"] = [{"type": "recall", "title": "Sáng: nhắc lại câu đến hạn, tối đa 30 phút (không học câu mới)", "minutes": 30, "id_n": 200},
                        {"type": "self", "title": "Sáng: lướt lại Đề ôn sát đề của cô (câu hay sai) + đọc ghi chú, viết ra giấy điều đang lo 10 phút", "minutes": 25, "id_n": 201},
                        {"type": "exam_day", "title": "CHIỀU THI. Nghỉ ngơi, ăn trưa no, đến sớm. Làm câu dễ trước, không bỏ trống câu nào.", "minutes": 5, "id_n": 202}]
        html.append([iso, 120, [[t["minutes"], "s" if t["type"] == "recall" else "o", t["title"]] for t in day["tasks"]], "Sáng ôn nhẹ · chiều thi"])
    else:
        rows = []
        seq = list(P[iso])
        if any(x not in (REC, SKIP) and x[0]["type"] == "exam" for x in seq):
            k = next((i for i, x in enumerate(seq) if x not in (REC, SKIP) and x[0]["type"] == "exam"), 0)
            seq.insert(k, "GUIDE")
        for i, it in enumerate(seq):
            if it == SKIP:
                continue
            if it == REC:
                n = int(round(LOAD[iso])); m = max(10, int(round(n * 0.35 / 5.0) * 5))
                if iso in TRIP:
                    task = {"type": "recall", "title": f"Nhắc lại trên điện thoại ~20 phút nếu tiện (không bắt buộc). Khoảng {n} câu đến hạn, làm được bao nhiêu thì làm.", "minutes": 20}
                elif iso in CAP:
                    task = {"type": "recall", "title": CAP[iso][2], "minutes": CAP[iso][1]}
                elif n == 0:
                    task = {"type": "recall", "title": "Nhắc lại câu đến hạn (nếu có)", "minutes": 10}
                else:
                    task = {"type": "recall", "title": f"Nhắc lại câu đến hạn (khoảng {n} câu, đáp án đã đảo) · chia nhỏ trong ngày được", "minutes": m}
                kind = "s"
            elif it == "GUIDE":
                task = {"type": "self", "guide": True, "title": "Đọc 4 bước làm 1 câu trước khi học bài mới (1 phút)", "minutes": 2}; kind = "o"
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
