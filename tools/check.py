"""Kiểm tra trước khi đưa lên: lịch không vượt giờ, đủ bài, không trùng id, dữ liệu 240 câu đúng. Cách dùng: python3 tools/check.py work"""
import collections, json, re, sys
W = sys.argv[1] if len(sys.argv) > 1 else "work"
S = json.load(open(f"{W}/data/schedule.json")); IDX = {x["num"]: x for x in json.load(open(f"{W}/data/exams/index.json"))}
F = json.load(open(f"{W}/data/formulas.json"))
err = []
ids = set()
for d in S:
    tot = sum(t["minutes"] for t in d["tasks"])
    if tot > d["budget"]: err.append(f"{d['date']}: {tot} phút > rảnh {d['budget']}")
    for t in d["tasks"]:
        k = (d["date"], t.get("id_n"))
        if k in ids: err.append(f"trùng id {k}")
        ids.add(k)
        if t["type"] in ("exam", "relearn") and t.get("ref") not in IDX: err.append(f"{d['date']}: bộ {t.get('ref')} không có")
learn = collections.Counter((t.get("ref"), t.get("part")) for d in S for t in d["tasks"] if t["type"] == "exam" and d["date"] >= "2026-11-14")
need = [(n, "1-50") for n in list(range(30, 42)) + list(range(20, 28)) + [16, 19]] + [(28, "1-25"), (28, "26-50")]
miss = [k for k in need if k not in learn]
if miss: err.append(f"thiếu bài học mới: {miss}")
dup = [k for k, v in learn.items() if v > 1]
if dup: err.append(f"học mới bị lặp: {dup}")
n240 = 0
for n in range(30, 42):
    for q in json.load(open(f"{W}/data/exams/de{n}.json"))["questions"]:
        n240 += 1
        if len(q["options"]) != 3 or q["answer"] not in "ABC": err.append(f"de{n}#{q['num']} sai số đáp án")
        if f"de{n}#{q['num']}" not in F: err.append(f"de{n}#{q['num']} thiếu công thức")
if n240 != 240: err.append(f"240 câu của cô chỉ có {n240}")
print("OK: không có lỗi" if not err else "LỖI:\n- " + "\n- ".join(err))
for d in S:
    if d["date"] >= "2026-11-14":
        print(d["date"], d["wd"], f"{sum(t['minutes'] for t in d['tasks'])}/{d['budget']} phút")
