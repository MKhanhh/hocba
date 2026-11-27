"""Tạo tools/azota.json: mỗi bài trong app = 1 đề Azota (định dạng "Tự soạn đề": *A. = đáp án đúng, Hướng dẫn giải = mẹo).
Cách dùng: python3 tools/azota_gen.py work"""
import json, os, re, sys
W = sys.argv[1] if len(sys.argv) > 1 else "work"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "azota.json")
M = json.load(open(f"{W}/data/meo.json"))
idx = {x["num"]: x for x in json.load(open(f"{W}/data/exams/index.json"))}
plain = lambda s: re.sub(r"\*\*(.+?)\*\*", r"\1", s or "").replace("*", "")
def sent(text, num):
    i = text.find(f"({num})")
    a = max(text.rfind(". ", 0, i), text.rfind("? ", 0, i), text.rfind("! ", 0, i), text.rfind("\n", 0, i)); a = 0 if a < 0 else a + 1
    m = re.search(r"[.?!](\s|$)", text[i + 4:]); b = len(text) if not m else i + 4 + m.start() + 1
    t = re.sub(r"\((\d+)\)\s*_{2,}", lambda x: "_____" if x.group(1) == str(num) else f"({x.group(1)}) ___", text[a:b].strip())
    return re.sub(r"\s+", " ", t)
out = {}
for n in list(range(30, 42)) + [28, 24, 25, 26, 27, 20, 21, 22, 23] + list(range(57, 63)):
    d = json.load(open(f"{W}/data/exams/de{n}.json")); qs = d["questions"]; P = d.get("passages") or {}
    parts = [("1-25", [q for q in qs if int(q["num"]) <= 25]), ("26-36", [q for q in qs if int(q["num"]) > 25])] if n == 28 else [("all", qs)]
    for pk, ql in parts:
        L, sol = [], []
        if 20 <= n <= 23 or n in (61, 62):
            p = P.get("reading") or next(iter(P.values()), {}); pt = p.get("text", "") if isinstance(p, dict) else p
            L += ["Phần 1. Đọc đoạn văn rồi trả lời câu hỏi", re.sub(r"\n+", " ", pt).strip()]
        for i, q in enumerate(ql, 1):
            t = sent(P["cloze"]["text"], int(q["num"])) if (24 <= n <= 27 or n == 60) else \
                ((q.get("prompt", "") + " ") if n == 28 else "") + (q.get("text") or q.get("stem_en") or "")
            L.append(f"Câu {i}. " + re.sub(r"\s+", " ", t).strip())
            L += [f"\t{'*' if 'ABCD'[j] == q['answer'] else ''}{'ABCD'[j]}. {o.strip()}" for j, o in enumerate(q["options"])]
            sol.append(f"Câu {i}: " + plain(M.get(f"de{n}#{q['num']}") or q.get("short") or q.get("easy")))
        name = idx[n]["name"] if n != 28 else f"Biến đổi câu của cô · câu {'1–25' if pk == '1-25' else '26–36'}"
        out[f"{n}:{pk}"] = {"name": "Học Bá · " + name, "count": len(ql),
                            "text": "\n".join(L) + "\n------HẾT------\nHướng dẫn giải\n" + "\n".join(sol)}
json.dump(out, open(OUT, "w"), ensure_ascii=False, indent=0)
print(len(out), "đề →", OUT)
