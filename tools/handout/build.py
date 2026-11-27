"""Tạo 6 bộ "Đề ôn sát đề" (de57–de62) từ tools/handout/raw.py + extra.py, thêm vào index.json và meo.json.
Câu trùng y hệt 240 câu / 36 câu biến đổi câu: lấy lại phần dịch + giải thích có sẵn.
Cách dùng: python3 tools/handout/build.py work"""
import copy, glob, json, os, re, sys
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
import raw, extra  # noqa: E402
W = sys.argv[1] if len(sys.argv) > 1 else "work"
nz = lambda s: re.sub(r"[^a-z0-9]", "", (s or "").lower().replace("’", "'").replace("neighbours", "neighbors"))
# ngân hàng: ưu tiên 240 câu + biến đổi câu
bank = {}
order = [f"{W}/data/exams/de{n}.json" for n in list(range(30, 42)) + [28]]
skip = {f"{W}/data/exams/de{n}.json" for n in range(57, 63)}
for f in order + sorted(set(glob.glob(f"{W}/data/exams/de*.json")) - set(order) - skip):
    d = json.load(open(f))
    for q in d["questions"]:
        t = q.get("text") or q.get("stem_en") or ""
        if t:
            bank.setdefault(nz(t), []).append((d["id"], q))
MEO = json.load(open(f"{W}/data/meo.json"))
NOTE = ("Đề ôn cô gửi 26/11 (file \"Ôn tập AVCD 3\", phần đầu). Cô dặn: đề này sát đề thi nhất, khoảng 30 câu (7 điểm) ra y hệt. "
        "Đáp án theo chữ đỏ trong file; câu file không tô đỏ do nhóm chuyên gia giải và kiểm tra lại.")
PL = {"vocab": "Từ vựng", "grammar": "Ngữ pháp", "transform": "Biến đổi câu", "cloze": "Điền từ", "reading": "Đọc hiểu"}

def base(num, part, text, options, ans, label):
    return {"num": num, "part": part, "part_label": PL[part], "bonus": False,
            "prompt": "Chọn câu có nghĩa giống câu gốc nhất:" if part == "transform" else "",
            "text": text, "stem_en": text, "options": options, "answer": ans, "why_original": "", "chunks": [],
            "vi_question": "", "vi_full": "", "options_vi": ["" for _ in options], "short": "", "easy": "", "super": "",
            "why_not": [], "tip": "", "read_aloud": "", "type_tag": "", "flag": "", "ai": True, "g": "VOCAB",
            "teacher": label}

def fill(q, key, sec, orig, meos, eid):
    """Lấy phần có sẵn từ câu trùng (nếu có), rồi phần nhóm viết (extra.X) ghi đè."""
    ans_txt = q["options"]["ABCD".index(q["answer"])]
    src = None
    for bid, bq in bank.get(nz(q["text"]), []):
        if nz(bq["options"]["ABCD".index(bq["answer"])]) == nz(ans_txt):
            src = (bid, bq); break
    if src:
        bid, bq = src
        for k in ("chunks", "vi_question", "vi_full", "short", "easy", "super", "tip", "g", "type_tag"):
            if bq.get(k): q[k] = copy.deepcopy(bq[k])
        bvi = {nz(o): v for o, v in zip(bq["options"], bq.get("options_vi") or [])}
        q["options_vi"] = [bvi.get(nz(o), "") for o in q["options"]]
        if [nz(o) for o in bq["options"]] == [nz(o) for o in q["options"]]:
            q["why_not"] = copy.deepcopy(bq.get("why_not") or [])
        q["read_aloud"] = bq.get("read_aloud") or ""
        q["why_original"] = f"Câu này giống câu {bq.get('teacher') and 'của cô ' + bq['teacher'] or bid}."
        m = MEO.get(f"{bid}#{bq['num']}")
        if m: meos[f"{eid}#{q['num']}"] = m
    x = extra.X.get((sec, orig))
    if x:
        vi, ovi, why, meo = x
        q["vi_question"] = q["vi_question"] or vi
        if not any(q["options_vi"]): q["options_vi"] = ovi
        else: q["options_vi"] = [a or b for a, b in zip(q["options_vi"], ovi)]
        if not q["short"]: q["short"] = q["easy"] = q["super"] = why
        meos[f"{eid}#{q['num']}"] = meo
    if not q["read_aloud"] and q["part"] in ("vocab", "grammar"):
        q["read_aloud"] = re.sub(r"_{2,}", ans_txt, q["text"].replace("___ you ever ___", "Have you ever seen"))
    if q["part"] in ("vocab", "grammar") and not q.get("g"): q["g"] = "VOCAB"
    return src is not None

def main():
    meos, exams, idx_add, stats = {}, {}, [], {}
    # 57 Từ vựng, 58 Ngữ pháp, 59 Biến đổi câu
    for num, sec, L, part, name in ((57, "V", raw.V, "vocab", "Đề ôn sát đề · 1. Từ vựng"),
                                    (58, "G", raw.G, "grammar", "Đề ôn sát đề · 2. Ngữ pháp"),
                                    (59, "T", raw.T, "transform", "Đề ôn sát đề · 3. Biến đổi câu")):
        eid = f"de{num}"; qs = []; hit = 0
        for i, row in enumerate(L, 1):
            orig, text, opts, ans = row
            label = f"Đề ôn sát đề · câu {orig}" + (" (phần biến đổi câu)" if sec == "T" else "")
            q = base(i, part, text, opts, ans, label)
            if sec == "G": q["g"] = "GRAMMAR"
            if sec == "T": q["g"] = "TRANSFORM"
            hit += fill(q, (sec, orig), sec, orig, meos, eid)
            qs.append(q)
        exams[num] = {"id": eid, "num": num, "name": name, "kind": "handout", "note": NOTE, "source": "builtin", "complete": True, "questions": qs}
        stats[eid] = (len(qs), hit)
    # 60 Điền từ
    text = re.sub(r"\((\d+)\) ________", lambda m: f"({int(m.group(1)) - 30}) ________", raw.CLOZE)
    qs = []
    for i, (orig, opts, ans) in enumerate(raw.C, 1):
        q = base(i, "cloze", "", opts, ans, f"Đề ôn sát đề · câu {orig}")
        q["g"] = "CLOZE"; q["tip"] = "Đọc cả câu có chỗ trống, xem chữ gợi ý ngay trước và sau chỗ trống."
        fill(q, ("C", orig), "C", orig, meos, "de60"); qs.append(q)
    exams[60] = {"id": "de60", "num": 60, "name": "Đề ôn sát đề · 4. Điền từ: Jane Austen", "kind": "handout", "note": NOTE,
                 "passages": {"cloze": {"title": raw.CLOZE_TITLE, "text": text}},
                 "passages_vi": {"cloze": {"text": extra.PASSAGE_VI["C"]}}, "source": "builtin", "complete": True, "questions": qs}
    # 61, 62 Đọc hiểu
    for num, which, title, ptxt, pvi, name in ((61, 1, raw.R1_TITLE, raw.R1, extra.PASSAGE_VI["R1"], "Đề ôn sát đề · 5. Đọc: Bay of Fundy"),
                                               (62, 2, raw.R2_TITLE, raw.R2, extra.PASSAGE_VI["R2"], "Đề ôn sát đề · 6. Đọc: Cool or crazy")):
        qs = []
        for orig, w, text, opts, ans in raw.R:
            if w != which: continue
            q = base(len(qs) + 1, "reading", text, opts, ans, f"Đề ôn sát đề · câu {orig}")
            q["g"] = "R_DETAIL"; q["tip"] = "Đọc câu hỏi trước, gạch chân từ khóa, tìm đúng từ đó trong bài rồi mới chọn."
            fill(q, ("R", orig), "R", orig, meos, f"de{num}"); qs.append(q)
        exams[num] = {"id": f"de{num}", "num": num, "name": name, "kind": "handout", "note": NOTE,
                      "passages": {"reading": {"title": title, "text": ptxt}}, "passages_vi": {"reading": {"text": pvi}},
                      "source": "builtin", "complete": True, "questions": qs}
    for num, ex in exams.items():
        json.dump(ex, open(f"{W}/data/exams/de{num}.json", "w"), ensure_ascii=False, indent=1)
    idx = [x for x in json.load(open(f"{W}/data/exams/index.json")) if x["num"] not in exams]
    idx += [{"id": ex["id"], "num": n, "name": ex["name"], "kind": "handout", "count": len(ex["questions"])} for n, ex in sorted(exams.items())]
    json.dump(idx, open(f"{W}/data/exams/index.json", "w"), ensure_ascii=False, indent=1)
    # mẹo: ghi vào tools/meo/handout.json (merge.py gộp chung)
    json.dump(meos, open(os.path.join(H, "..", "meo", "handout.json"), "w"), ensure_ascii=False, indent=0)
    print("bộ:", {e: f"{n} câu, {h} câu trùng ngân hàng" for e, (n, h) in stats.items()}, "| mẹo:", len(meos))

main()
