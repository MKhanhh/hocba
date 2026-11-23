"""Gộp mẹo "Thấy ... → chọn ..." (tools/meo/*.json) vào <work>/data/meo.json và kiểm tra đáp án trong mẹo khớp đề.
Cách dùng: python3 tools/meo/merge.py work"""
import glob, json, os, re, sys
W = sys.argv[1] if len(sys.argv) > 1 else "work"
H = os.path.dirname(os.path.abspath(__file__))
M = {}
for f in sorted(glob.glob(f"{H}/*.json")):
    M.update(json.load(open(f)))
norm = lambda s: s.replace("’", "'").lower()
err = []
for n in list(range(24, 29)) + list(range(30, 42)):
    for q in json.load(open(f"{W}/data/exams/de{n}.json"))["questions"]:
        k = f"de{n}#{q['num']}"
        m = M.get(k)
        if not m: err.append(f"thiếu mẹo {k}"); continue
        c = re.findall(r"chọn (?:câu có )?\*\*(.+?)\*\*", m)
        ans = q["options"]["ABCD".index(q["answer"])]
        if not c or (n == 28 and not all(p.strip() in norm(ans) for p in norm(c[0]).split("...") if p.strip())) \
                or (n != 28 and norm(c[0]) != norm(ans)):
            err.append(f"{k}: mẹo chọn {c} nhưng đáp án là {ans}")
json.dump(M, open(f"{W}/data/meo.json", "w"), ensure_ascii=False, indent=0)
print(f"{len(M)} mẹo" + (" · OK" if not err else " · LỖI:\n- " + "\n- ".join(err)))
