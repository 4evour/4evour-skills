#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""deslop_check.py — 中文内容 AI 腔检测（advisory，不是判决）

用法:
    python deslop_check.py 文章.md
    cat 文章.md | python deslop_check.py -

报的是嫌疑不是罪证：自然语境下的命中可以放过。
B站口语稿：口语路标（其实/对/然后/好）密度高于书面是正常的，连词类命中按口语阈值放行。
"""

import re
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

FENCE = re.compile(r"^```")


def strip_inline_code(line: str) -> str:
    return re.sub(r"`[^`]*`", "", line)


def load_lines(path: str):
    if path == "-":
        return sys.stdin.read().splitlines()
    with open(path, encoding="utf-8", errors="replace") as f:
        return f.read().splitlines()


def numbered_body(lines):
    """yield (lineno, text) with fenced code blocks blanked out."""
    in_fence = False
    for i, raw in enumerate(lines, 1):
        if FENCE.match(raw.strip()):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        yield i, strip_inline_code(raw)


PATTERNS = [
    (
        "对仗反射「不是X而是Y」(全文应<=1处)",
        1,
        [re.compile(r"不是[^。？！\n]{2,30}[，,]而是")],
    ),
    (
        "对仗变体「不只是/更是」",
        1,
        [re.compile(r"不只是[^。？！\n]{2,30}(更|而是)"), re.compile(r"与其说[^。？！\n]{2,30}不如说")],
    ),
    (
        "段末升华元评论",
        0,
        [
            re.compile(r"(这说明|这展示了|这证明了|这更说明|这体现了|由此可见|综上所述|这代表着|更能(说明|体现)|但它们决定了|决定了[^。]{2,20}看起来是)")
        ],
    ),
    (
        "假揭示(看似X本质Y/真正的关键)",
        0,
        [
            re.compile(r"看似[^。！？\n]{2,20}(本质|实则|背后)"),
            re.compile(r"(本质|实则)(上?是|在于)"),
            re.compile(r"归根结底"),
            re.compile(r"真正的?(关键|问题|答案|差距|价值)"),
            re.compile(r"深层的?(原因|逻辑|需求)"),
        ],
    ),
    (
        "模糊归因(业内人士/研究表明)",
        0,
        [
            re.compile(r"(业内人士|普遍认为|有观点认为|专家表示|网友纷纷)"),
            re.compile(r"研究表明[^：:，。]"),
        ],
    ),
    (
        "公式化格言/底层逻辑",
        0,
        [
            re.compile(r"底层逻辑"),
            re.compile(r"拉开(了)?差距"),
            re.compile(r"是[^。，！？]{1,10}的(语言|货币|镜子|基石|答案|注脚)"),
        ],
    ),
    (
        "回应未提出的反对(先叠甲)",
        0,
        [
            re.compile(r"(我并不是说|我无意|别误会|先叠个甲|我不是要说)"),
        ],
    ),
    (
        "拒绝假选项(有人可能会想…但)",
        0,
        [
            re.compile(r"(有人|你)可能会(说|想|觉得)[^。]{0,40}但"),
        ],
    ),
    (
        "聊天残留(希望有帮助/以上就是)",
        0,
        [
            re.compile(r"希望[^。]{0,10}帮助"),
            re.compile(r"以上就是[^。]{0,20}"),
            re.compile(r"让我们(开始|进入|一起)"),
        ],
    ),
    (
        "AI高频套话",
        0,
        [
            re.compile(r"值得注意的是"),
            re.compile(r"(深入|深度)的?(探讨|解析|剖析)"),
            re.compile(r"进行了?[^。，]{0,8}(优化|分析|解析|测试|评估|重构|处理)"),
            re.compile(r"(赋能|抓手)"),
            re.compile(r"说到底[，,]"),
        ],
    ),
    (
        "开头套话(首行)",  # 特殊处理: 只查前 5 个非空行
        -5,
        [re.compile(r"^(随着|在当今|众所周知|在这个[^的]{1,6}的时代)")],
    ),
    (
        "首先-其次-最后结构",
        0,
        [re.compile(r"首先[^。！？]{4,60}[。！？][^。！？]{0,20}其次")],
    ),
    (
        "bold起手+句号(应改为逗号衔接)",
        0,
        [re.compile(r"^\*\*[^*]+\*\*。")],
    ),
    (
        "破折号——",
        0,
        [re.compile(r"——")],
    ),
    (
        "短引号抽象名词(人工复核)",
        -1,  # 只列出,不计分
        [re.compile(r"[「\"“]([^」\"”]{2,8})[」\"”]")],
    ),
]


def check_fragment_runs(body):
    """连续>=5行、每行<25字且以句号/分号结尾(或无标点)的碎句清单。"""
    hits = []
    run = []
    for lineno, text in body:
        s = text.strip()
        is_item = bool(re.match(r"^([-*+]|\d+\.)\s*", s))
        payload = re.sub(r"^([-*+]|\d+\.)\s*", "", s)
        if (is_item or s) and 0 < len(payload) <= 25 and not re.search(r"[？！:：]$", payload):
            run.append((lineno, payload))
        else:
            if len(run) >= 5:
                hits.append(run)
            run = []
    if len(run) >= 5:
        hits.append(run)
    return hits


def check_sentence_rhythm(body):
    """段落内句子长度过于均一(std<=4 且句数>=4)。"""
    hits = []
    for lineno, text in body:
        s = text.strip()
        if len(s) < 60 or s.startswith(("#", "|", ">", "- ", "* ")):
            continue
        parts = [p for p in re.split(r"[。！？]", s) if p.strip()]
        if len(parts) < 4:
            continue
        lens = [len(p.strip()) for p in parts]
        mean = sum(lens) / len(lens)
        std = (sum((x - mean) ** 2 for x in lens) / len(lens)) ** 0.5
        if max(lens) - min(lens) <= 8 and std <= 4:
            hits.append((lineno, lens))
    return hits


def check_punchline_runs(body):
    """单行内连续>=3个<=12字的短句(金句连发/表演性碎片)。"""
    hits = []
    for lineno, text in body:
        s = text.strip()
        if len(s) < 15 or s.startswith(("#", "|", ">", "- ", "* ")):
            continue
        parts = [p.strip() for p in re.split(r"[。！？]", s) if p.strip()]
        run = []
        best = []
        for p in parts:
            if 0 < len(p) <= 12:
                run.append(p)
                if len(run) > len(best):
                    best = run[:]
            else:
                run = []
        if len(best) >= 3:
            hits.append((lineno, best))
    return hits


def check_repeated_openers(body):
    """单行内连续>=3句以相同代词开头(我/我们/它/这/该)。"""
    hits = []
    for lineno, text in body:
        s = text.strip()
        if len(s) < 30 or s.startswith(("#", "|", ">", "- ", "* ")):
            continue
        parts = [p.strip() for p in re.split(r"[。！？]", s) if p.strip()]
        opens = []
        for p in parts:
            m = re.match(r"^(我|我们|它|她们|他们|这个|该)", p)
            opens.append(m.group(1) if m else None)
        i = 0
        while i < len(opens):
            j = i
            while j < len(opens) and opens[j] == opens[i] and opens[i] is not None:
                j += 1
            if opens[i] is not None and j - i >= 3:
                hits.append((lineno, opens[i], j - i))
            i = max(j, i + 1)
    return hits


def check_label_lists(body):
    """连续>=3个「- **标签：** 解释」式列表项。"""
    hits = []
    run = []
    for lineno, text in body:
        s = text.strip()
        if re.match(r"^[-*+]\s*\*\*[^*]{1,12}(?:[:：]\*\*|\*\*[:：])", s):
            run.append((lineno, s))
        else:
            if len(run) >= 3:
                hits.append(run)
            run = []
    if len(run) >= 3:
        hits.append(run)
    return hits


def check_bold_overuse(body):
    """单行>=4处加粗(bold滥用,重点全加粗=没有重点)。"""
    return [(n, len(re.findall(r"\*\*[^*]+\*\*", t.strip()))) for n, t in body
            if len(re.findall(r"\*\*[^*]+\*\*", t.strip())) >= 4]


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    lines = load_lines(sys.argv[1])
    body = list(numbered_body(lines))
    nonempty = [(n, t) for n, t in body if t.strip()][:5]

    total = 0
    print("=" * 56)
    print(" AI 腔检测报告（嫌疑清单，人工裁决）")
    print("=" * 56)

    for name, limit, regexes in PATTERNS:
        if limit == -5:  # 只查开头几行
            found = [(n, m.group(0)) for n, t in nonempty for rx in regexes for m in rx.finditer(t)]
        else:
            found = [
                (n, m.group(0)) for n, t in body for rx in regexes for m in rx.finditer(t)
            ]
        if limit == -1:
            # 引号短词: 只报出现>=2次的(重复使用才是腔调)
            from collections import Counter

            cnt = Counter(w for _, w in found)
            dup = {w: c for w, c in cnt.items() if c >= 2 and not re.match(r"^[\w\s.-]+$", w)}
            if dup:
                print(f"\n[?] {name}:")
                for w, c in sorted(dup.items(), key=lambda x: -x[1]):
                    print(f"    \"{w}\" x{c}")
            continue
        flag = ""
        if limit == 1:
            flag = "  <-- 超限!" if len(found) > 1 else ""
        elif limit == 0:
            flag = ""  # 计数型,人工判断
        if found:
            total += len(found)
            print(f"\n[{len(found) if limit == 0 else ('OK' if limit == 1 and len(found) <= 1 else len(found))}] {name}{flag}")
            for n, snippet in found[:6]:
                show = snippet if snippet.strip() else "(空)"
                print(f"    L{n}: {show[:60]}")
            if len(found) > 6:
                print(f"    ... 共 {len(found)} 处")

    frags = check_fragment_runs(body)
    if frags:
        total += sum(len(r) for r in frags)
        print(f"\n[{len(frags)}处] 碎句排比清单(连续>=5行短条目,关键项需补'为什么/代价/坑'):")
        for run in frags[:3]:
            head = run[0][0]
            sample = " / ".join(p for _, p in run[:3])
            print(f"    L{head}起({len(run)}条): {sample[:70]}...")

    rhythm = check_sentence_rhythm(body)
    if rhythm:
        print(f"\n[{len(rhythm)}处] 句子长度过于均一(段落内长短差<=8字):")
        for n, lens in rhythm[:5]:
            print(f"    L{n}: 各句字数 {lens}")

    punch = check_punchline_runs(body)
    if punch:
        total += len(punch)
        print(f"\n[{len(punch)}处] 金句连发(单行内连续>=3个<=12字短句):")
        for n, run in punch[:5]:
            print(f"    L{n}: {' / '.join(run[:5])}")

    rep = check_repeated_openers(body)
    if rep:
        total += len(rep)
        print(f"\n[{len(rep)}处] 句首重复主语(连续>=3句以相同代词开头):")
        for n, w, c in rep[:5]:
            print(f"    L{n}: 「{w}」开头连续 {c} 句")

    labels = check_label_lists(body)
    if labels:
        total += len(labels)
        print(f"\n[{len(labels)}处] 「标签:解释」式列表(连续>=3项,考虑合并成自然段):")
        for run in labels[:3]:
            head = run[0][0]
            print(f"    L{head}起({len(run)}项): {run[0][1][:60]}")

    bold = check_bold_overuse(body)
    if bold:
        print(f"\n[?] bold滥用(单行>=4处加粗,人工复核):")
        for n, c in bold[:5]:
            print(f"    L{n}: {c} 处加粗")

    print("\n" + "=" * 56)
    print(f" 合计命中: {total} 处。逐条核对：自然语境的命中可放过。")
    print(" 提醒: 人工复核五项——升华句是否全删、失败叙事是否>=2处、")
    print("       引号抽象名词是否换成具体所指、假揭示/模糊归因是否落到事实、")
    print("       信息账本回扫(数字/专名/限定词是否与原素材一致)。")


if __name__ == "__main__":
    main()
