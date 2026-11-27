# Gắn dịch-theo-cụm (tools/chunks_add.py) vào work/data/exams/*.json và kiểm tra khớp câu gốc.
import json, re, sys, pathlib
sys.path.insert(0, "tools"); from chunks_add import C
ROOT = pathlib.Path("work/data/exams")
def cloze_sentence(text, num):
    i = text.find(f"({num})")
    if i < 0: return ""
    ms = list(re.finditer(r"[.?!]\s+|\n+", text[:i])); a = ms[-1].end() if ms else 0
    m = re.search(r"[.?!](\s|$)|\n", text[i + 4:]); b = len(text) if not m else i + 4 + m.start() + 1
    return text[a:b].strip()
def nz(s): return re.sub(r"_+", "_", re.sub(r"[^a-z0-9_()]", "", s.lower()))
def norm_blank(s): return re.sub(r"_{2,}", "___", s)
bad = 0; done = {}
for key, (spec, vi) in C.items():
    eid, n = key.split("#"); n = int(n)
    p = ROOT / f"{eid}.json"; d = done.get(eid) or json.loads(p.read_text()); done[eid] = d
    q = next(x for x in d["questions"] if int(x["num"]) == n)
    stem = q.get("text") or q.get("stem_en") or ""
    if not stem.strip():
        sent = cloze_sentence(d["passages"][q["part"]]["text"], n)
        stem = re.sub(r"\(%d\)\s*_*" % n, "___ ", sent)
    stem = norm_blank(re.sub(r"\(\d+\)\s*_{2,}", lambda m: m.group(0).split(")")[0] + ")", stem))
    ch = []
    for part in spec.split(" | "):
        en, v, r = [x.strip() for x in part.split(" = ")]
        assert r in ("ai","lam","cai","odau","khi","them"), (key, r)
        ch.append({"en": en, "vi": v, "role": r})
    joined = " ".join(c["en"] for c in ch)
    a, b = nz(joined), nz(stem)
    if a != b:
        bad += 1; print("LỆCH", key, "\n  gốc :", stem, "\n  cụm :", joined)
    q["chunks"] = ch
    if vi: q["vi_question"] = vi
if "--write" in sys.argv and not bad:
    for eid, d in done.items(): (ROOT / f"{eid}.json").write_text(json.dumps(d, ensure_ascii=False, indent=1))
    print("ĐÃ GHI", len(C), "câu vào", len(done), "đề")
print("lệch:", bad, "/", len(C))
