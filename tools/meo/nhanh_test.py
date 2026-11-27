"""Thi thử máy móc: chỉ dùng các dòng ⚡ (work/data/nhanh.json) để làm cả 439 câu.
Với mỗi câu: tìm mọi dòng ⚡ có chữ "Thấy" xuất hiện trong câu hỏi → mỗi dòng chỉ ra đáp án nào → phải ra đúng 1 đáp án và là đáp án đúng."""
import json, re, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent)); import nhanh
S = json.loads(pathlib.Path("work/data/nhanh.json").read_text())
Q = nhanh.load(); n = lambda s: " " + " ".join(nhanh.words(s.lower().replace("’", "'"))) + " "
def rule(t):
    cue = re.search(r"Thấy \*\*(.+?)\*\* →", t).group(1)
    tail = t.split("→", 1)[1]
    exact = "đúng y" in tail
    picks = re.findall(r"\*\*(.+?)\*\*", tail)
    return [n(x).strip() for x in cue.split("...")], [n(x).strip() for x in picks], exact
R = {k: rule(v) for k, v in S.items()}
bad = 0
for q in Q:
    st = n(q["stem"]); chosen = set()
    for k, (cue, picks, exact) in R.items():
        o = next(x for x in Q if x["k"] == k)
        if o["group"] != q["group"]: continue
        pos, ok = 0, True
        for c in cue:
            i = st.find(f" {c} ", pos)
            if i < 0: ok = False; break
            pos = i + len(c)
        if not ok: continue
        hits = [i for i, op in enumerate(q["opts"]) if (n(op).strip() == picks[0] if exact else all(f" {p} " in n(op) for p in picks))]
        chosen.update(q["opts"][i] for i in hits) if hits else chosen.add("(không có đáp án nào khớp: " + k + ")")
    if chosen != {q["ans"]}:
        bad += 1; print("SAI", q["k"], "| chọn:", chosen, "| đúng:", q["ans"])
print(f"Thi thử máy móc: {len(Q) - bad}/{len(Q)} câu đúng")
