"""Dòng ⚡ NHÌN PHÁT CHỌN cho mọi câu trong lịch: "Thấy <chữ ở câu hỏi> → chọn <chữ ở đáp án>".
Máy tự tìm rồi tự kiểm tra:
  - chữ ở câu hỏi: chỉ câu này có (trong cả 413 câu; câu đọc/điền từ: trong cùng bài),
  - chữ ở đáp án: chỉ đáp án đúng có (3 đáp án kia không có).
Sửa tay ở dict TAY nếu chữ máy chọn khó nhớ. Chạy: python3 tools/meo/nhanh.py → tools/nhanh.json"""
import json, re, sys, pathlib
EX = pathlib.Path("work/data/exams")
IDS = list(range(20, 29)) + list(range(30, 42)) + list(range(57, 63))
STOP = set("a an the to of in on at for and or but is are was were be been am i you he she it we they my your his her our their this that these those do does did not no ___ with as by from so if than then there here have has had will would can could should must may might me him them us what which who when where why how one very too".split())
TAY = {   # "deNN#n": ("chữ ở câu hỏi", "chữ ở đáp án") – sửa tay cho dễ nhớ hơn (máy vẫn kiểm tra lại)
"de20#3": ("special", "two"), "de20#4": ("except", "Campaigns"), "de21#6": ("designer", "bright"),
"de22#3": ("family of four", "1 640 pounds"), "de22#5": ("This text is about", "costs"),
"de24#1": ("at ___ once", "least"), "de24#4": ("has to ___", "offer"), "de24#8": ("___ hour", "rush"),
"de25#2": ("to the ___", "worst"), "de25#13": ("mainly ___", "tourists and business travelers"),
"de27#3": ("heart ___", "disease"), "de30#1": ("keys", "lose"), "de31#15": ("end of class", "give"),
"de34#16": ("she asked ___", "politely"), "de36#6": ("pay raise", "got"), "de38#2": ("call my husband", "should"),
"de39#10": ("doll", "upset"), "de28#2": ("talk to your teacher", "were you, I would"),
"de59#12": ("talk to your teacher", "were you, I would"), "de28#21": ("most talented", "more + than"),
"de59#9": ("most talented", "more + than"), "de41#5": ("nervous if", "'d be"),
}
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from tim import T as _BDC   # biến đổi câu: dùng mẹo "tìm chữ" nhóm đã viết
for _k, (_c, _f) in _BDC.items():
    if _k not in TAY: TAY[_k] = (" ... ".join(_c), " + ".join(_f))

def words(s): return re.findall(r"___|'?[^\W_]+(?:'[^\W_]+)*", s.replace("’", "'"))
def low(s): return " ".join(w.lower() for w in words(s))
def has(hay, gram): return f" {gram} " in f" {hay} "

def cloze_sentence(text, num):
    i = text.find(f"({num})")
    if i < 0: return ""
    ms = list(re.finditer(r"[.?!]\s+|\n+", text[:i])); a = ms[-1].end() if ms else 0
    m = re.search(r"[.?!](\s|$)|\n", text[i + 4:]); b = len(text) if not m else i + 4 + m.start() + 1
    s = text[a:b].strip()
    s = re.sub(r"\(%d\)\s*_*" % num, " ___ ", s)
    return re.sub(r"\(\d+\)\s*_*", " zzkhac ", s)   # chỗ trống câu khác: không lấy làm chữ nhận diện

def load():
    Q = []
    for n in IDS:
        d = json.loads((EX / f"de{n}.json").read_text())
        for q in d["questions"]:
            stem = q.get("text") or q.get("stem_en") or ""
            if not stem.strip() and q["part"] in ("cloze", "reading"):
                stem = cloze_sentence(d["passages"][q["part"]]["text"], int(q["num"]))
            group = f"de{n}" if q["part"] in ("cloze", "reading") else "ALL"
            ans = q["options"]["ABCD".index(q["answer"])]
            Q.append(dict(k=f"de{n}#{q['num']}", stem=stem, group=group, ans=ans, opts=q["options"], part=q["part"]))
    return Q

GENERIC = set("around also things thing important any big high near it's difficult people time new good many mentioned passage according paragraph writer main idea word mean means following true false text story usually often always really every day today soon now still just only some more most much other another way like get got make made go going take well right best better however think yet that's anything coming about first lot this see everyone i'm i've i'll you're it's there's".split())
DF = {}

def grams(ws, nmax=4, stop_ok=False):
    for n in range(1, nmax + 1):
        for i in range(len(ws) - n + 1):
            g = ws[i:i + n]
            if g == ["___"] or "zzkhac" in g: continue
            if not stop_ok:
                if all(w in STOP or w in GENERIC for w in g): continue
                if n > 1 and (g[0] in STOP or g[-1] in STOP) and "___" not in (g[0], g[-1]): continue
            yield n, i, " ".join(g)

def salience(q, g):
    """Điểm càng nhỏ càng dễ nhớ: tên riêng > danh từ dài hiếm > cụm sát chỗ trống."""
    ws = g.split(); raw = words(q["stem"])
    proper = any(w[0].isupper() and i > 0 for i, w in enumerate(raw) if w.lower() in ws)
    content = [w for w in ws if w not in STOP and w not in GENERIC and w != "___"]
    return (len(ws), 0 if proper else 1, min([DF.get(w, 0) for w in content] or [99]), -max([len(w) for w in content] or [0]))

def ans_grams(q):
    """Chữ để chọn: cả đáp án ngắn → cụm ngắn có nghĩa → cụm chỉ gồm từ nhỏ → đúng y nguyên đáp án ("= ...")."""
    a = low(q["ans"])
    if len(a.split()) <= 4: yield a
    G = list(grams(a.split(), 6, stop_ok=True))
    for _, _, g in sorted(G, key=lambda x: (all(w in STOP for w in x[2].split()), x[0])): yield g
    yield "= " + a

def ok_pick(o, pk):
    if pk.startswith("= "):
        e = pk[2:]
        return low(o["ans"]) == e and sum(low(x) == e for x in o["opts"]) == 1
    ps = [low(x) for x in pk.split(" + ")]
    hit = lambda t: all(has(low(t), x) for x in ps)
    return hit(o["ans"]) and not any(hit(x) for x in o["opts"] if low(x) != low(o["ans"]))

def cue_in(stem, cue):
    t = low(stem); pos = 0
    for part in [x.strip() for x in cue.split("...")]:
        i = f" {t} ".find(f" {low(part)} ", pos)
        if i < 0: return False
        pos = i + len(part)
    return True

def choose(q, Q):
    me = low(q["stem"]); peers = [o for o in Q if o is not q and o["group"] == q["group"]]
    for strict in (True, False):
        best = None
        for n, i, g in grams(me.split()) if strict else grams(me.split(), 6, stop_ok=True):
            C = [o for o in peers if cue_in(o["stem"], g)]
            if len(C) > 3: continue
            for pk in ans_grams(q):
                if ok_pick(q, pk) and all(ok_pick(o, pk) for o in C):
                    sc = (len(C) > 0, pk.startswith("= "), salience(q, g))
                    if best is None or sc < best[0]: best = (sc, g, pk)
                    break
        if best: return best[1], best[2]
    return None, None

def check(q, Q, cue, pk):
    errs = []
    if not cue_in(q["stem"], cue): errs.append("câu hỏi không có chữ này")
    if not ok_pick(q, pk): errs.append("chữ chọn không riêng của đáp án đúng")
    for o in Q:
        if o is not q and o["group"] == q["group"] and cue_in(o["stem"], cue) and not ok_pick(o, pk):
            errs.append("lẫn với " + o["k"])
    return errs

def orig(text, gram):
    """Lấy lại đúng chữ gốc (hoa/thường, dấu phẩy, ’) trong câu cho dễ nhận ra."""
    toks = gram.split()
    pat = r"[\s,;:.!?\"“”()-]*".join(r"_+" if t == "___" else re.escape(t).replace("'", "['’]") for t in toks)
    m = re.search(r"(?<![\w'’])" + pat + r"(?![\w])", text, re.I)
    return re.sub(r"\s+", " ", m.group(0).strip()) if m else gram

def main():
    Q = load(); out = {}; bad = 0
    for q in Q:
        for w in set(low(q["stem"]).split()): DF[w] = DF.get(w, 0) + 1
    for q in Q:
        cue, pk = TAY.get(q["k"]) or (None, None)
        if not cue or check(q, Q, cue, pk):
            cue, pk = choose(q, Q)
        if not cue or not pk:
            bad += 1; print("KHÔNG TÌM ĐƯỢC", q["k"], cue, pk, "|", q["stem"][:70]); continue
        e = check(q, Q, cue, pk)
        if e: bad += 1; print("LỖI", q["k"], cue, "→", pk, e); continue
        out[q["k"]] = {"cue": cue, "pick": pk}
    print(len(out), "câu ·", bad, "lỗi")
    show = {}
    for q in Q:
        if q["k"] not in out: continue
        c, p = out[q["k"]]["cue"], out[q["k"]]["pick"]
        cue = " ... ".join(orig(q["stem"], x.strip()) for x in c.split("..."))
        if p.startswith("= "):
            tail = f"chọn đúng y **{q['ans'].strip().rstrip('.')}**"
        elif " + " in p:
            tail = "chọn câu có " + " + ".join(f"**{orig(q['ans'], x.strip())}**" for x in p.split(" + "))
        else:
            tail = f"chọn **{orig(q['ans'], p)}**"
        show[q["k"]] = f"Thấy **{cue}** → {tail}"
    if "--write" in sys.argv and not bad:
        pathlib.Path("tools/nhanh.json").write_text(json.dumps(out, ensure_ascii=False, indent=0) + "\n")
        pathlib.Path("work/data/nhanh.json").write_text(json.dumps(show, ensure_ascii=False, indent=0) + "\n")
        print("đã ghi tools/nhanh.json + work/data/nhanh.json")
    return show
    return out

if __name__ == "__main__":
    o = main()
    if "--show" in sys.argv:
        for k, v in o.items(): print(k, "|", v)
