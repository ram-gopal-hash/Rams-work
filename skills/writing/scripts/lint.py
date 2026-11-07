#!/usr/bin/env python3
"""
lint.py - mechanical checks for the writing skill.

Reads a text/markdown file, reports pattern hits and rhythm statistics.
Diagnostic only. It does not rewrite anything and it does not pass or fail
a document; a human reads the report and decides.

Usage:
    python3 lint.py draft.md
    python3 lint.py draft.md --register bank
    python3 lint.py draft.md --profile ../reference/voice_profile.json
    python3 lint.py draft.md --json

Stdlib only. Python 3.8+.
"""

import argparse
import json
import re
import statistics
import sys
import unicodedata
from pathlib import Path

# ---------------------------------------------------------------------------
# Pattern tables. Merged from humanizer (Wikipedia signs-of-AI list) and
# anti-ai-writing sections 4, 5, 8.
# ---------------------------------------------------------------------------

BANNED_VOCAB = """
delve realm harness unlock tapestry paradigm cutting-edge revolutionize
intricate intricacies showcasing crucial pivotal surpass meticulously vibrant
unparalleled underscore leverage synergy innovative game-changer testament
commendable meticulous highlight emphasize boast groundbreaking align foster
showcase enhance holistic garner accentuate pioneering trailblazing unleash
versatile transformative redefine seamless optimize scalable robust breakthrough
empower streamline frictionless elevate adaptive effortless data-driven
insightful proactive mission-critical visionary disruptive reimagine
unprecedented intuitive leading-edge synergize democratize accelerate
state-of-the-art dynamic immersive predictive plug-and-play turnkey future-proof
paradigm-shifting supercharge enduring interplay captivate landscape
""".split()

# Words above that are legitimate in Ram's domains and only flagged as
# "soft" hits, since solar/finance writing uses them literally.
SOFT_VOCAB = {
    "align", "scalable", "robust", "optimize", "dynamic", "predictive",
    "accelerate", "transparent", "integrated", "proprietary", "valuable",
    "landscape", "elevate", "enhance",
}

PHRASE_PATTERNS = {
    "copula avoidance": [
        r"\bserves as\b", r"\bstands as\b", r"\bmarks a\b", r"\brepresents a\b",
        r"\bboasts a\b", r"\bfeatures a\b", r"\boffers a\b",
        r"\bplays a (?:key |vital |crucial |significant )?role\b",
        r"\bhelps to\b", r"\baims to\b", r"\bseeks to\b", r"\bfunctions as\b",
    ],
    "dead opening": [
        r"\bIn today'?s\b", r"\bIt is important to note\b", r"\bIt'?s worth noting\b",
        r"\bIn order to\b", r"\bLet'?s (?:dive in|explore|unpack)\b",
        r"\bAt the end of the day\b", r"\bMoving forward\b",
        r"\bTo put this in perspective\b", r"\bWhat makes this particularly\b",
        r"\bIt goes without saying\b", r"\bMost people don'?t realize\b",
        r"\bIn this (?:article|section|report), I will\b",
        r"\bNobody is talking about\b",
    ],
    "dead transition": [
        r"(?m)^\s*Furthermore\b", r"(?m)^\s*Additionally\b", r"(?m)^\s*Moreover\b",
        r"\bThat (?:said|being said)\b", r"\bWith that in mind\b",
        r"\bIt is also worth mentioning\b", r"\bOn top of that\b",
    ],
    "engagement bait": [
        r"\bLet that sink in\b", r"\bRead that again\b", r"\bFull stop\b",
        r"\bThis changes everything\b", r"\bAre you paying attention\b",
        r"\bYou are not ready for\b",
    ],
    "significance inflation": [
        r"\ba (?:key |major )?turning point\b", r"\ba pivotal moment\b",
        r"\bsetting the stage for\b", r"\bmarking a significant\b",
        r"\bbroader implications\b", r"\bis a testament to\b",
        r"\bindelible mark\b", r"\bdeeply rooted\b", r"\bevolving landscape\b",
    ],
    "participle padding": [
        r",\s+(?:highlighting|underscoring|emphasizing|reflecting|symbolizing|"
        r"contributing to|cultivating|fostering|encompassing|showcasing|ensuring|"
        r"paving the way|opening the door)\b",
    ],
    "vague attribution": [
        r"\b(?:Industry (?:reports|observers)|Observers have|Experts (?:argue|believe|say)|"
        r"Some critics argue|Many believe|It is widely (?:believed|held))\b",
    ],
    "cutoff disclaimer": [
        r"\bAs of my last (?:update|training)\b", r"\bBased on available information\b",
        r"\bWhile specific details are (?:limited|scarce)\b",
        r"\bI do not have real-?time access\b",
    ],
    "assistant chatter": [
        r"\bI hope this helps\b", r"\bGreat question\b", r"\bHappy to help\b",
        r"\bLet me know if you\b", r"\bWould you like me to\b",
        r"(?m)^\s*(?:Certainly|Of course)[!,]", r"\bYou'?re absolutely right\b",
    ],
    "hype": [
        r"\b10x your\b", r"\bgame-?changer\b", r"\bsupercharge\b",
        r"\bunlock (?:the |your )?(?:potential|power|value)\b",
    ],
}

# Negative parallelism / rejected-frame constructions. Regex is approximate
# here; expect false positives on legitimate contrast. Read the line before
# acting on the flag.
NEGPAR_PATTERNS = [
    r"\b(?:This|That|It) is\s?n(?:'|\u2019)?t\s+[^.;]{2,60}[.;]\s+(?:This|That|It)(?:'|\u2019)?s\b",
    r"\bnot (?:just|only|merely|simply) about\b",
    r"\bnot only\b[^.]{2,80}\bbut (?:also )?\b",
    r"\bIt(?:'|\u2019)?s not\b[^.]{2,60}\bit(?:'|\u2019)?s\b",
    r"\bLess\b[^.,]{2,40},\s*more\b",
    r"\bForget\b[^.]{2,40}\.\s*(?:Focus|Think|Look)\b",
    r"\bThe (?:real|actual|deeper|hidden|overlooked) (?:issue|problem|question|answer|goal)\b",
    r"\bThe (?:question|problem|issue|answer|goal) is not\b",
    r"\bIt was never about\b[^.]{2,60}\bIt was always\b",
    r"\b(?:While|Although) [^.,]{2,50} (?:may seem|appears?|looks like|sounds)\b",
    r"\bAt first glance\b", r"\bOn the surface\b",
    r"\b(?:Most people|Many) (?:think|assume|believe)\b",
    r"\bConventional wisdom (?:says|holds)\b",
    r"\bX gets (?:all )?the attention\b",
    r"\b(?:is dead|is over)\.\s+[A-Z][^.]{2,40}is the future\b",
    # Trailing / appositive negation: assertion first, negated foil tacked on
    # ("X is Y, not Z"). Added Sept 2026 after 13 instances shipped undetected
    # through seven versions of a partner proposal. Every pattern above this
    # line is a LEADING form; none of them fire on the trailing shape.
    r"[a-z][^.;:]{10,90},\s+not\s+(?:a |an |the |on |by |for |to |in |at )?[a-z][^.;,]{2,45}[.;,]",
    r"\bonly\b[^.;]{2,60},\s+not\b",
]

ANALOGY_PATTERNS = [
    r"\bThink of (?:it|this) as\b", r"\bIt(?:'|\u2019)?s (?:kind of )?like\b",
    r"\bImagine (?:a|an|you|if)\b", r"\bPicture (?:a|an|the)\b",
    r"\b(?:works|acts) like\b",
    r"\bthe (?:engine|fuel|backbone|foundation|fabric|heartbeat|DNA|glue|"
    r"bridge|lens|roadmap|north star|flywheel) (?:of|for|between|that)\b",
]

METAPHOR_VERBS = """
sanded bolted stripped stitched woven layered carved baked injected fueled
sparked anchored framed mapped distilled unpacked crystallized sharpened
surfaced amplified channeled threaded sculpted molded cemented bridged
""".split()

HEDGES = """
arguably possibly potentially perhaps somewhat relatively fairly rather quite
generally typically often usually essentially basically virtually largely
""".split()

# Second-generation tells (patterns.md section 9). Reported as a density
# metric, not as sight-bans: these are legitimate words in bank/dpr/legal
# and only become a fault in bulk.
SECOND_GEN_VOCAB = """
significant significantly increasingly substantial substantially considerable
notable notably marked consequences implications ramifications factors aspects
elements dimensions considerations developments dynamics framework frameworks
methodology methodologies parameter parameters mechanism mechanisms criteria
approach context scope capacity capability capabilities interdependence
reindustrialisation reindustrialization proliferation differentiation
convergence optimisation optimization prioritisation prioritization
""".split()

# Latinate word -> plain replacement (patterns.md section 10). Suppressed in
# contract/legal, where several are terms of art.
LATINATE = {
    "utilise": "use", "utilize": "use", "utilisation": "use",
    "commence": "start", "terminate": "end", "purchase": "buy",
    "demonstrate": "show", "facilitate": "help", "sufficient": "enough",
    "subsequent": "later", "additional": "more", "attempt": "try",
    "obtain": "get", "assist": "help", "indicate": "show",
    "component": "part", "numerous": "many", "initiate": "start",
    "finalise": "finish", "finalize": "finish", "ascertain": "find out",
    "endeavour": "try", "endeavor": "try", "remuneration": "pay",
}
LATINATE_PHRASES = [(r"\bprior to\b", "before"), (r"\bin the event that\b", "if"),
                    (r"\bwith regard to\b", "about"), (r"\bin excess of\b", "over")]

# Nominalisation: weak verb followed by an abstract noun within a few words.
NOMINAL_SUFFIX = r"[A-Za-z]{3,}(?:tions?|ments?|ances?|ences?|ities|ity|isms?|isations?|izations?)"
NOMINAL_PATTERNS = [
    r"\b(?:undertook|undertake[sn]?|conduct(?:s|ed|ing)?|perform(?:s|ed|ing)?|"
    r"carr(?:y|ies|ied) out|provid(?:e|es|ed|ing)|achiev(?:e|es|ed|ing)|"
    r"effect(?:s|ed)?|facilitat(?:e|es|ed)|enabl(?:e|es|ed)|mak(?:e|es)|"
    r"gav?e|giv(?:es|ing))\s+(?:a|an|the|)\s*" + NOMINAL_SUFFIX + r"\b",
    r"\bthere (?:is|are|was|were)\s+(?:a|an|no|some|)\s*" + NOMINAL_SUFFIX + r"\b",
    r"\bthe\s+" + NOMINAL_SUFFIX + r"\s+of\b",
]

# Registers where structural formatting is required and must not be flagged.
STRUCTURED_REGISTERS = {"bank", "dpr", "legal", "contract"}
# Registers where abstraction and nominalisation density are relaxed: hits
# are still listed, the density warning is not raised. See registers.md,
# "The 2026 checks".
RELAXED_DENSITY_KEYS = {"abstraction_per_100w", "nominalisation_per_100w"}
ALL_REGISTERS = ["general", "bank", "dpr", "legal", "contract",
                 "investor", "article", "post", "email"]


# ---------------------------------------------------------------------------
# Text handling
# ---------------------------------------------------------------------------

def strip_code_and_tables(text):
    """Blank out fenced code, inline code and markdown table rows, keeping
    line numbering intact so reported line numbers stay accurate."""
    lines = text.split("\n")
    out, in_fence = [], False
    for line in lines:
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            out.append("")
            continue
        if in_fence:
            out.append("")
            continue
        if re.match(r"^\s*\|.*\|\s*$", line):
            out.append("")
            continue
        out.append(re.sub(r"`[^`]*`", "", line))
    return "\n".join(out)


def prose_only(text):
    """Drop headings, list markers and blockquote markers for rhythm stats."""
    kept = []
    for line in text.split("\n"):
        if re.match(r"^\s*#{1,6}\s", line):
            continue
        line = re.sub(r"^\s*(?:[-*+]|\d+\.)\s+", "", line)
        line = re.sub(r"^\s*>\s?", "", line)
        kept.append(line)
    return "\n".join(kept)


SENT_END = re.compile(r"(?<=[.!?])\s+(?=[A-Z\"'(\[])")


def sentences(text):
    chunks = []
    for para in re.split(r"\n\s*\n", text):
        para = " ".join(para.split())
        if not para:
            continue
        chunks.extend(s for s in SENT_END.split(para) if s.strip())
    return chunks


def words(s):
    return re.findall(r"[A-Za-z][A-Za-z'\u2019-]*", s)


def line_of(text, pos):
    return text.count("\n", 0, pos) + 1


def snippet(text, start, end, width=64):
    line_start = text.rfind("\n", 0, start) + 1
    line_end = text.find("\n", end)
    if line_end == -1:
        line_end = len(text)
    frag = text[line_start:line_end].strip()
    if len(frag) <= width:
        return frag
    off = max(0, start - line_start - width // 3)
    return ("..." if off else "") + frag[off:off + width].strip() + "..."


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------

def find_regex(text, patterns, label):
    hits = []
    for pat in patterns:
        for m in re.finditer(pat, text, flags=re.IGNORECASE):
            hits.append({
                "check": label,
                "line": line_of(text, m.start()),
                "match": m.group(0).strip()[:60],
                "context": snippet(text, m.start(), m.end()),
            })
    return hits


def check_vocab(text):
    hits = []
    for w in BANNED_VOCAB:
        pat = r"\b" + re.escape(w).replace(r"\-", "-") + r"(?:s|es|ed|ing|ly)?\b"
        for m in re.finditer(pat, text, flags=re.IGNORECASE):
            hits.append({
                "check": "banned vocab" + (" (soft)" if w in SOFT_VOCAB else ""),
                "line": line_of(text, m.start()),
                "match": m.group(0),
                "context": snippet(text, m.start(), m.end()),
            })
    return hits


def check_metaphor_verbs(text):
    hits = []
    for w in METAPHOR_VERBS:
        for m in re.finditer(r"\b" + w + r"\b", text, flags=re.IGNORECASE):
            hits.append({
                "check": "metaphor verb",
                "line": line_of(text, m.start()),
                "match": m.group(0),
                "context": snippet(text, m.start(), m.end()),
            })
    return hits


def check_punctuation(text, register, report_quotes=False):
    hits = []
    for m in re.finditer(r"\u2014", text):
        hits.append({"check": "em dash", "line": line_of(text, m.start()),
                     "match": "\u2014", "context": snippet(text, m.start(), m.end())})
    for m in (re.finditer(r"[\u201c\u201d\u2018\u2019]", text) if report_quotes else []):
        if m.group(0) == "\u2019" and re.match(r"[A-Za-z]", text[m.end():m.end() + 1] or ""):
            continue  # apostrophe inside a word
        hits.append({"check": "curly quote", "line": line_of(text, m.start()),
                     "match": m.group(0), "context": snippet(text, m.start(), m.end())})
    for i, ch in enumerate(text):
        if unicodedata.category(ch) == "So" and ord(ch) > 0x2100:
            hits.append({"check": "emoji", "line": line_of(text, i),
                         "match": ch, "context": snippet(text, i, i + 1)})
    if register not in STRUCTURED_REGISTERS:
        for m in re.finditer(r"(?m)^\s*[-*+]\s+\*\*[^*]{2,40}\*\*\s*:", text):
            hits.append({"check": "inline-header list", "line": line_of(text, m.start()),
                         "match": m.group(0).strip()[:40],
                         "context": snippet(text, m.start(), m.end())})
    return hits


FRAGMENT_PATTERNS = [
    # Noun phrase, comma, noun phrase, no finite verb: "Two independent
    # routes, same answer". Compression into cadence; the version with the
    # verb is almost always the better sentence.
    r"(?:^|[.;:|]\s+)[A-Z][\w\s'-]{4,45},\s+(?:same|no|not|nothing|none|one|two|both|all|never|always|every)\b[^.;:|]{0,40}",
    r"(?:^|[.;:|]\s+)(?:No|Not|Nothing|Same|Both|Neither)\s+[\w\s'-]{2,40}[.;|]",
]


def check_repeated_foil(text):
    """The same negated foil used more than once is a tic, even where each
    instance would pass the keep/cut test on its own."""
    hits, seen = [], {}
    for m in re.finditer(r",\s+not\s+(?:a |an |the |on |by |for |to |in |at )?([\w'\u2019-]+(?:\s[\w'\u2019-]+){0,2})",
                         text, flags=re.IGNORECASE):
        key = m.group(1).lower().rstrip(".,;")
        seen.setdefault(key, []).append(m)
    for key, ms in seen.items():
        if len(ms) > 1:
            for m in ms:
                hits.append({"check": "repeated foil",
                             "line": line_of(text, m.start()),
                             "match": ("x%d  ...not %s" % (len(ms), key))[:60],
                             "context": snippet(text, m.start(), m.end())})
    return hits


def check_rule_of_three(text):
    hits = []
    pat = r"\b([\w'\u2019-]+(?:\s[\w'\u2019-]+){0,2}),\s([\w'\u2019-]+(?:\s[\w'\u2019-]+){0,2}),\sand\s([\w'\u2019-]+(?:\s[\w'\u2019-]+){0,2})\b"
    for m in re.finditer(pat, text):
        hits.append({"check": "rule of three", "line": line_of(text, m.start()),
                     "match": m.group(0)[:60], "context": snippet(text, m.start(), m.end())})
    return hits


def check_second_gen(text):
    """Abstract quantifiers, borrowed-authority nouns, rare-register words.
    Density matters, not presence. Flagged soft; read the line."""
    hits = []
    for w in SECOND_GEN_VOCAB:
        for m in re.finditer(r"\b" + w + r"\b", text, flags=re.IGNORECASE):
            hits.append({"check": "second-gen vocab (soft)",
                         "line": line_of(text, m.start()), "match": m.group(0),
                         "context": snippet(text, m.start(), m.end())})
    return hits


def check_latinate(text, register):
    if register in {"contract", "legal"}:
        return []
    hits = []
    for w, plain in LATINATE.items():
        for m in re.finditer(r"\b" + w + r"(?:s|d|ed|ing)?\b", text, flags=re.IGNORECASE):
            hits.append({"check": "latinate", "line": line_of(text, m.start()),
                         "match": f"{m.group(0)} -> {plain}",
                         "context": snippet(text, m.start(), m.end())})
    for pat, plain in LATINATE_PHRASES:
        for m in re.finditer(pat, text, flags=re.IGNORECASE):
            hits.append({"check": "latinate", "line": line_of(text, m.start()),
                         "match": f"{m.group(0)} -> {plain}",
                         "context": snippet(text, m.start(), m.end())})
    return hits


def check_nominalisation(text):
    hits = []
    for pat in NOMINAL_PATTERNS:
        for m in re.finditer(pat, text, flags=re.IGNORECASE):
            hits.append({"check": "nominalisation",
                         "line": line_of(text, m.start()),
                         "match": m.group(0).strip()[:60],
                         "context": snippet(text, m.start(), m.end())})
    return hits


def check_and_stacking(sents, text):
    """Sentences carrying three or more coordinating 'and's."""
    hits = []
    for s in sents:
        n = len(re.findall(r"\band\b", s, flags=re.IGNORECASE))
        if n >= 3:
            pos = text.find(s[:40])
            hits.append({"check": "and-stacking",
                         "line": line_of(text, pos) if pos >= 0 else 0,
                         "match": f"{n} x 'and' in one sentence",
                         "context": s[:64] + ("..." if len(s) > 64 else "")})
    return hits


def check_repeated_openings(sents):
    """Three or more sentences opening with the same first two words."""
    buckets = {}
    for s in sents:
        w = words(s)[:2]
        if len(w) < 2:
            continue
        key = " ".join(x.lower() for x in w)
        buckets.setdefault(key, []).append(s[:50])
    return [{"check": "repeated opening", "line": 0,
             "match": f'"{k}" x{len(v)}', "context": v[0]}
            for k, v in buckets.items() if len(v) >= 3]


def rhythm(sents, paras):
    lens = [len(words(s)) for s in sents if words(s)]
    plens = [len(words(p)) for p in paras if words(p)]
    out = {"sentences": len(lens), "paragraphs": len(plens)}
    if len(lens) >= 2:
        mean = statistics.mean(lens)
        sd = statistics.pstdev(lens)
        out.update({
            "sent_mean": round(mean, 1),
            "sent_sd": round(sd, 1),
            "sent_cv": round(sd / mean, 3) if mean else 0,
            "sent_min": min(lens),
            "sent_max": max(lens),
            "short_pct": round(100 * sum(1 for x in lens if x <= 8) / len(lens), 1),
            "long_pct": round(100 * sum(1 for x in lens if x >= 30) / len(lens), 1),
        })
    if len(plens) >= 2:
        pmean = statistics.mean(plens)
        out["para_cv"] = round(statistics.pstdev(plens) / pmean, 3) if pmean else 0
        out["para_mean"] = round(pmean, 1)
    return out


def concreteness(text):
    w = words(text)
    n = len(w) or 1
    nums = len(re.findall(r"(?<![A-Za-z])\d[\d,.]*(?:%|\s?(?:kW|kWp|MW|MWp|Rs|INR|Cr|lakh|crore))?", text))
    caps = len([x for x in w if x[0].isupper()])
    month = r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?"
    dates = len(re.findall(
        rf"\b\d{{1,2}}\s+{month}"          # 12 February (day-first)
        rf"|\b{month}\s+\d{{1,4}}"          # February 12 / March 2026
        rf"|\b{month}\b"                    # bare month name
        r"|\b(?:19|20)\d{2}\b"              # bare year
        r"|\b(?:Q[1-4]|FY\s?\d{2,4})\b"     # Q3, FY26
        r"|\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b", text))
    hedge = sum(len(re.findall(r"\b" + h + r"\b", text, flags=re.IGNORECASE)) for h in HEDGES)
    abstract = sum(len(re.findall(r"\b" + w + r"\b", text, flags=re.IGNORECASE))
                   for w in SECOND_GEN_VOCAB)
    nominal = len(re.findall(r"\b" + NOMINAL_SUFFIX + r"\b", text))
    return {
        "words": n,
        "numbers_per_100w": round(100 * nums / n, 2),
        "dates_per_100w": round(100 * dates / n, 2),
        "capitalised_per_100w": round(100 * caps / n, 2),
        "hedges_per_100w": round(100 * hedge / n, 2),
        "commas_per_100w": round(100 * text.count(",") / n, 2),
        "semicolons_per_100w": round(100 * text.count(";") / n, 2),
        "parens_per_100w": round(100 * text.count("(") / n, 2),
        "quotes_per_100w": round(100 * len(re.findall(r'["\u201c]', text)) / n, 2),
        "and_per_100w": round(100 * len(re.findall(r"\band\b", text, flags=re.IGNORECASE)) / n, 2),
        "abstraction_per_100w": round(100 * abstract / n, 2),
        "nominalisation_per_100w": round(100 * nominal / n, 2),
    }


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------

THRESHOLDS = {
    "sent_cv": (0.45, "sentence length too uniform (metronome rhythm)"),
    "para_cv": (0.25, "paragraph length too uniform"),
    "numbers_per_100w": (1.0, "low numeric density - few verifiable specifics"),
    "hedges_per_100w": (2.0, "high hedge density", "above"),
    "commas_per_100w": (4.0, "under-punctuated - long unbroken clauses"),
    "parens_per_100w": (0.10, "no parentheses - asides and arithmetic not nested"),
    "and_per_100w": (4.5, "coordination-heavy - clauses chained with 'and'", "above"),
    "abstraction_per_100w": (2.5, "abstraction density - vague quantifiers and consequence nouns", "above"),
    "nominalisation_per_100w": (6.0, "nominalisation density - verbs buried in nouns", "above"),
}


def build_report(path, register, profile=None, report_quotes=False):
    raw = Path(path).read_text(encoding="utf-8", errors="replace")
    text = strip_code_and_tables(raw)
    body = prose_only(text)
    sents = sentences(body)
    paras = [p for p in re.split(r"\n\s*\n", body) if p.strip()]

    hits = []
    hits += check_vocab(text)
    for label, pats in PHRASE_PATTERNS.items():
        hits += find_regex(text, pats, label)
    hits += find_regex(text, NEGPAR_PATTERNS, "negative parallelism")
    hits += find_regex(text, ANALOGY_PATTERNS, "analogy")
    hits += check_metaphor_verbs(text)
    hits += check_punctuation(text, register, report_quotes)
    hits += find_regex(text, FRAGMENT_PATTERNS, "verbless fragment")
    hits += check_repeated_foil(text)
    hits += check_rule_of_three(text)
    hits += check_second_gen(text)
    hits += check_latinate(text, register)
    hits += check_nominalisation(text)
    hits += check_and_stacking(sents, body)
    hits += check_repeated_openings(sents)
    hits.sort(key=lambda h: (h["line"], h["check"]))

    r = rhythm(sents, paras)
    c = concreteness(body)

    # Density rates are unstable on short samples; suppress those warnings
    # below 200 words rather than reporting noise.
    DENSITY_KEYS = {"commas_per_100w", "semicolons_per_100w", "parens_per_100w",
                    "and_per_100w", "abstraction_per_100w",
                    "nominalisation_per_100w", "numbers_per_100w",
                    "hedges_per_100w"}
    short_sample = c["words"] < 200
    relaxed = RELAXED_DENSITY_KEYS if register in STRUCTURED_REGISTERS else set()

    def skip(key):
        return (short_sample and key in DENSITY_KEYS) or key in relaxed

    warnings = []
    if short_sample:
        warnings.append(f"sample is {c['words']} words; density checks suppressed below 200")
    if relaxed:
        warnings.append(f"register={register}: abstraction and nominalisation density relaxed "
                        f"(hits still listed; see registers.md)")
    for key, spec in THRESHOLDS.items():
        limit, msg = spec[0], spec[1]
        above = len(spec) > 2
        val = r.get(key, c.get(key))
        if val is None:
            continue
        if skip(key):
            continue
        if (val > limit) if above else (val < limit):
            warnings.append(f"{msg} ({key}={val}, threshold {'>' if above else '<'}{limit})")

    if profile:
        for key, target in profile.get("targets", {}).items():
            val = r.get(key, c.get(key))
            if val is None or skip(key):
                continue
            lo, hi = target["low"], target["high"]
            if not (lo <= val <= hi):
                warnings.append(f"off voice profile: {key}={val}, your range {lo}-{hi}")
        for key, target in profile.get("provisional_targets", {}).items():
            if key.startswith("_"):
                continue
            val = r.get(key, c.get(key))
            if val is None or skip(key):
                continue
            lo, hi = target["low"], target["high"]
            if not (lo <= val <= hi):
                warnings.append(
                    f"off provisional band (NOT calibrated on your corpus): "
                    f"{key}={val}, band {lo}-{hi}")

    counts = {}
    for h in hits:
        counts[h["check"]] = counts.get(h["check"], 0) + 1

    return {"file": str(path), "register": register, "rhythm": r,
            "concreteness": c, "counts": counts, "warnings": warnings, "hits": hits}


def render(rep, verbose):
    L = []
    L.append(f"lint: {rep['file']}   register={rep['register']}")
    L.append("=" * 68)
    r, c = rep["rhythm"], rep["concreteness"]
    L.append(f"{c['words']} words, {r.get('sentences', 0)} sentences, {r.get('paragraphs', 0)} paragraphs")
    if "sent_mean" in r:
        L.append(f"sentence length  mean {r['sent_mean']}  sd {r['sent_sd']}  "
                 f"cv {r['sent_cv']}  range {r['sent_min']}-{r['sent_max']}")
        L.append(f"  short (<=8w) {r['short_pct']}%   long (>=30w) {r['long_pct']}%")
    if "para_cv" in r:
        L.append(f"paragraph length mean {r['para_mean']}  cv {r['para_cv']}")
    L.append(f"density  numbers {c['numbers_per_100w']}/100w   dates {c['dates_per_100w']}/100w   "
             f"hedges {c['hedges_per_100w']}/100w")
    L.append(f"punctuation  commas {c['commas_per_100w']}   semicolons {c['semicolons_per_100w']}   "
             f"parens {c['parens_per_100w']}   quotes {c['quotes_per_100w']}  (per 100w)")
    L.append(f"2026 tells   and {c['and_per_100w']}   abstraction {c['abstraction_per_100w']}   "
             f"nominalisation {c['nominalisation_per_100w']}  (per 100w)")
    L.append("")

    if rep["counts"]:
        L.append("pattern hits")
        L.append("-" * 68)
        for k, v in sorted(rep["counts"].items(), key=lambda x: -x[1]):
            L.append(f"  {v:>4}  {k}")
    else:
        L.append("pattern hits: none")
    L.append("")

    if rep["warnings"]:
        L.append("warnings")
        L.append("-" * 68)
        for w in rep["warnings"]:
            L.append(f"  ! {w}")
        L.append("")

    if verbose and rep["hits"]:
        L.append("detail")
        L.append("-" * 68)
        for h in rep["hits"]:
            loc = f"L{h['line']}" if h["line"] else "--"
            L.append(f"  {loc:>6}  [{h['check']}]  {h['match']}")
            L.append(f"          {h['context']}")
    elif rep["hits"]:
        L.append(f"({len(rep['hits'])} hits; run with -v for line-by-line detail)")

    L.append("")
    L.append("Flags are candidates, not verdicts. Negative-parallelism and analogy")
    L.append("checks are regex approximations and will catch legitimate contrast.")
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser(description="Mechanical prose checks for the writing skill.")
    ap.add_argument("file")
    ap.add_argument("--register", default="general", choices=ALL_REGISTERS,
                    help="document class; structured registers suppress formatting flags")
    ap.add_argument("--profile", help="path to voice_profile.json")
    ap.add_argument("--json", action="store_true", help="emit JSON instead of a report")
    ap.add_argument("-v", "--verbose", action="store_true", help="line-by-line hits")
    ap.add_argument("--quotes", action="store_true",
                    help="also flag curly quotes (off by default: usually a Word/source artifact, not authored style)")
    a = ap.parse_args()

    if not Path(a.file).exists():
        sys.exit(f"lint: no such file: {a.file}")

    profile = None
    if a.profile and Path(a.profile).exists():
        profile = json.loads(Path(a.profile).read_text(encoding="utf-8"))

    rep = build_report(a.file, a.register, profile, a.quotes)
    print(json.dumps(rep, indent=2) if a.json else render(rep, a.verbose))


if __name__ == "__main__":
    main()
