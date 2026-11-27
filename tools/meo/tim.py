# Mẹo Biến đổi câu kiểu "Thấy (chữ ở đề) → tìm chữ (chỉ đáp án đúng có)".
# Chạy: python3 tools/meo/tim.py  → kiểm tra rồi ghi vào bdc.json (de28) và handout.json (de59).
import json, re, sys, pathlib
T = {
"de28#1": (["doesn't", "as hard as"], ["harder than"]),
"de28#2": (["should"], ["would"]),
"de28#3": (["the first time"], ["never visited"]),
"de28#4": (["tired, so I can't"], ["weren't"]),
"de28#5": (["started", "in 2010"], ["has worked", "since"]),
"de28#6": (["used to"], ["doesn't"]),
"de28#7": (["because the rain was heavy"], ["heavy rain"]),
"de28#8": (["was sick, but"], ["was sick"]),
"de28#9": (["with the idea of learning"], ["to learn"]),
"de28#10": (["a good idea to"], ["should"]),
"de28#11": (["I think", "will"], ["should"]),
"de28#12": (["use", "to cut"], ["for cutting"]),
"de28#13": (["unnecessary"], ["don't have to"]),
"de28#14": (["are you going to wear"], ["are you wearing"]),
"de28#15": (["studies hard to get"], ["she studies"]),
"de28#16": (["too heavy to lift"], ["couldn't"]),
"de28#17": (["used to live"], ["don't live"]),
"de28#18": (["cannot enter"], ["not allowed"]),
"de28#19": (["would rather rest than study"], ["I dislike studying"]),
"de28#20": (["noisy while he played"], ["noisily"]),
"de28#21": (["the most"], ["more", "than"]),
"de28#22": (["talks too much", "bored"], ["more bored"]),
"de28#23": (["difficult to understand"], ["understand the"]),
"de28#24": (["sorry when she heard"], ["to hear"]),
"de28#25": (["little"], ["much"]),
"de28#26": (["because the traffic was bad"], ["the bad traffic"]),
"de28#27": (["will increase"], ["likely to increase"]),
"de28#28": (["used to play"], ["doesn't"]),
"de28#29": (["cause"], ["lead to"]),
"de28#30": (["won't", "if she doesn't try"], ["without"]),
"de28#31": (["unusual"], ["different from"]),
"de28#32": (["Although"], ["Despite practicing"]),
"de28#33": (["They repaired"], ["was repaired"]),
"de28#34": (["needs to"], ["for him to"]),
"de28#35": (["were dancing when"], ["while"]),
"de28#36": (["not as expensive as yours"], ["more expensive"]),
"de59#1": (["has three members"], ["three people"]),
"de59#2": (["was reading", "when the lights went out"], ["while I was reading"]),
"de59#3": (["noisy while he played"], ["noisily"]),
"de59#4": (["Unless", "will fail"], ["will fail", "if you don't"]),
"de59#5": (["quiet while they waited"], ["quietly"]),
"de59#6": (["the first time"], ["never visited"]),
"de59#7": (["because the traffic was bad"], ["the bad traffic"]),
"de59#8": (["tired, so I can't"], ["weren't"]),
"de59#9": (["the most"], ["more", "than"]),
"de59#10": (["used to"], ["doesn't"]),
"de59#11": (["started", "in 2010"], ["has worked", "since"]),
"de59#12": (["should"], ["were you, I would"]),
"de59#13": (["doesn't", "as hard as"], ["harder than"]),
"de59#14": (["are you having", "tonight"], ["going to have"]),
"de59#15": (["because the rain was heavy"], ["heavy rain"]),
"de59#16": (["doesn't see", "very often"], ["hardly ever"]),
"de59#17": (["was sick, but"], ["was sick"]),
"de59#18": (["doesn't see", "very often"], ["hardly ever"]),
"de59#19": (["Russia is colder than Germany"], ["Germany isn't as cold"]),
"de59#20": (["and then I watched TV"], ["music. After that"]),
}
EX = pathlib.Path("work/data/exams")
def nz(s): return s.replace("’", "'").lower()
def text(k):
    cue, find = T[k]
    a = " ... ".join(cue)
    f = " + ".join(f"**{x}**" for x in find)
    return f"Thấy **{a}** → tìm câu có {f}" if len(find) > 1 else f"Thấy **{a}** → tìm chữ {f}"
bad = 0; out = {}
for k, (cue, find) in T.items():
    e, n = k.split("#"); d = json.loads((EX / f"{e}.json").read_text())
    q = next(x for x in d["questions"] if int(x["num"]) == int(n))
    stem = nz(q["text"]); opts = [nz(o) for o in q["options"]]; ai = "ABCD".index(q["answer"])
    for c in cue:
        if nz(c) not in stem: bad += 1; print("ĐỀ KHÔNG CÓ", k, c)
    if not all(nz(f) in opts[ai] for f in find): bad += 1; print("ĐÁP ÁN ĐÚNG KHÔNG CÓ", k, find)
    for i, o in enumerate(opts):
        if i != ai and all(nz(f) in o for f in find): bad += 1; print("ĐÁP ÁN SAI CŨNG CÓ", k, "ABCD"[i], o)
    out[k] = text(k)
print("lỗi:", bad, "/", len(T))
if bad: sys.exit(1)
if "--write" in sys.argv:
    for fn, pre in (("bdc.json", "de28#"), ("handout.json", "de59#")):
        p = pathlib.Path("tools/meo") / fn; m = json.loads(p.read_text())
        for k, v in out.items():
            if k.startswith(pre): m[k] = v
        p.write_text(json.dumps(m, ensure_ascii=False, indent=0) + "\n")
    print("đã ghi", len(out))
for k in ("de28#5", "de28#2", "de59#12"): print(k, out[k])
