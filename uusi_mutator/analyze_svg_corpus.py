import os
import re
import sys
import json
import math
import xml.etree.ElementTree as ET
from collections import defaultdict, Counter

# Usage:
# python analyze_svg_corpus.py <svg_corpus_dir> <known_strings_file> <output_py>

NUM_RE = re.compile(r"^[+-]?(?:\d+|\d*\.\d+)(?:[eE][+-]?\d+)?$")
PERCENT_RE = re.compile(r"^[+-]?(?:\d+|\d*\.\d+)%$")
HEX_COLOR_RE = re.compile(r"^#[0-9a-fA-F]{3,8}$")
URL_REF_RE = re.compile(r"^url\(#([^)]+)\)$")
HASH_REF_RE = re.compile(r"^#([A-Za-z_][\w:.-]*)$")
FUNC_RE = re.compile(r"^[A-Za-z_][\w.-]*\s*\(")

SVG_NS_SUFFIX = "}svg"

ENUM_CAP = 64
VALUE_SAMPLE_CAP = 128


def strip_ns(tag: str) -> str:
    if "}" in tag:
        return tag.split("}", 1)[1]
    return tag


def load_known_strings(path: str):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        text = f.read()
    pieces = []
    for line in text.splitlines():
        s = line.strip()
        if not s:
            continue
        pieces.append(s)
    return pieces


def known_match(value: str, known_strings):
    for s in known_strings:
        if value in s or s in value:
            return True
    return False


def looks_like_number(s: str) -> bool:
    return bool(NUM_RE.match(s) or PERCENT_RE.match(s))


def looks_like_color(s: str) -> bool:
    if HEX_COLOR_RE.match(s):
        return True
    low = s.lower().strip()
    if low in {
        "none", "currentcolor", "transparent", "black", "white", "red", "green",
        "blue", "yellow", "gray", "grey", "purple", "pink", "orange", "brown",
        "lime", "navy", "teal", "silver", "maroon", "aqua", "fuchsia"
    }:
        return True
    if low.startswith("rgb(") or low.startswith("rgba(") or low.startswith("hsl(") or low.startswith("hsla("):
        return True
    return False


def looks_like_transform(s: str) -> bool:
    low = s.strip()
    return any(low.startswith(prefix) for prefix in (
        "matrix(", "translate(", "scale(", "rotate(", "skewx(", "skewy("
    ))


def looks_like_path(s: str) -> bool:
    low = s.strip()
    if not low:
        return False
    letters = set("MmLlHhVvCcSsQqTtAaZz")
    return any(ch in letters for ch in low) and any(ch.isdigit() for ch in low)


def looks_like_points(s: str) -> bool:
    s = s.strip()
    if "," not in s:
        return False
    toks = s.replace("\n", " ").split()
    good = 0
    for tok in toks[:8]:
        if "," in tok:
            a, _, b = tok.partition(",")
            if looks_like_number(a) and looks_like_number(b):
                good += 1
    return good >= 1


def looks_like_viewbox(s: str) -> bool:
    toks = s.replace(",", " ").split()
    return len(toks) == 4 and all(looks_like_number(t) for t in toks)


def looks_like_style(s: str) -> bool:
    return ":" in s and ";" in s


def looks_like_preserve_aspect_ratio(s: str) -> bool:
    vals = {
        "none", "xMinYMin", "xMidYMin", "xMaxYMin",
        "xMinYMid", "xMidYMid", "xMaxYMid",
        "xMinYMax", "xMidYMax", "xMaxYMax",
        "meet", "slice"
    }
    toks = s.split()
    return all(tok in vals for tok in toks)


def guess_value_type(attr: str, values):
    attr_low = attr.lower()

    if attr_low in {"d"}:
        return "path"
    if attr_low in {"points"}:
        return "points"
    if attr_low in {"transform", "gradienttransform", "patterntransform"}:
        return "transform"
    if attr_low in {"viewbox"}:
        return "viewbox"
    if attr_low in {"style"}:
        return "style"
    if attr_low in {"id"}:
        return "id"
    if attr_low in {"href", "xlink:href"}:
        return "href"
    if attr_low in {"fill", "stroke", "flood-color", "lighting-color", "stop-color", "color"}:
        return "paint"
    if attr_low in {"filter", "clip-path", "mask", "marker-start", "marker-mid", "marker-end"}:
        return "url_ref"

    sample = list(values)[:64]
    if sample and all(looks_like_number(v) for v in sample):
        if any("." in v or "e" in v.lower() or "%" in v for v in sample):
            return "number"
        return "integer"

    if sample and all(looks_like_color(v) for v in sample):
        return "paint"

    if sample and all(looks_like_transform(v) for v in sample):
        return "transform"

    if sample and all(looks_like_path(v) for v in sample):
        return "path"

    if sample and all(looks_like_points(v) for v in sample):
        return "points"

    if sample and all(looks_like_viewbox(v) for v in sample):
        return "viewbox"

    if sample and all(looks_like_preserve_aspect_ratio(v) for v in sample):
        return "preserveAspectRatio"

    # enum heuristic
    uniq = set(sample)
    if 1 <= len(uniq) <= 16:
        shortish = all(len(v) <= 40 for v in uniq)
        if shortish:
            return "enum"

    # url refs
    if sample and all(URL_REF_RE.match(v) or HASH_REF_RE.match(v) for v in sample):
        return "url_ref"

    # style-ish
    if sample and sum(looks_like_style(v) for v in sample) >= max(1, len(sample) // 2):
        return "style"

    return "string"


def main():
    if len(sys.argv) != 4:
        print("Usage: python analyze_svg_corpus.py <svg_corpus_dir> <known_strings_file> <output_py>")
        sys.exit(1)

    corpus_dir = sys.argv[1]
    known_strings_file = sys.argv[2]
    output_py = sys.argv[3]

    known_strings = load_known_strings(known_strings_file)

    tag_attrs = defaultdict(Counter)
    tag_children = defaultdict(Counter)
    attr_values = defaultdict(Counter)
    attr_known_hits = defaultdict(int)
    tag_seen = Counter()
    ids_seen = Counter()
    href_targets = Counter()
    parse_failures = 0

    for root_dir, _, files in os.walk(corpus_dir):
        for fn in files:
            if not fn.lower().endswith(".svg"):
                continue

            path = os.path.join(root_dir, fn)
            try:
                with open(path, "rb") as f:
                    data = f.read()
                text = data.decode("utf-8", errors="ignore")
                root = ET.fromstring(text)
            except Exception:
                parse_failures += 1
                continue

            for elem in root.iter():
                tag = strip_ns(elem.tag)
                tag_seen[tag] += 1

                for attr, val in elem.attrib.items():
                    a = strip_ns(attr)
                    tag_attrs[tag][a] += 1
                    attr_values[a][val] += 1
                    if known_match(val, known_strings):
                        attr_known_hits[a] += 1

                    if a == "id":
                        ids_seen[val] += 1

                    if a in {"href", "xlink:href", "fill", "stroke", "filter", "clip-path", "mask", "marker-start", "marker-mid", "marker-end"}:
                        m = URL_REF_RE.match(val)
                        if m:
                            href_targets[m.group(1)] += 1
                        elif HASH_REF_RE.match(val):
                            href_targets[val[1:]] += 1

                for child in list(elem):
                    ctag = strip_ns(child.tag)
                    tag_children[tag][ctag] += 1

    attr_types = {}
    attr_enums = {}
    attr_samples = {}

    for attr, counter in attr_values.items():
        values = [v for v, _ in counter.most_common(VALUE_SAMPLE_CAP)]
        attr_types[attr] = guess_value_type(attr, values)
        attr_samples[attr] = values[:32]

        if attr_types[attr] == "enum":
            attr_enums[attr] = values[:ENUM_CAP]
        else:
            # even for non-enums, preserve a few known short values if they look helpful
            short_values = [v for v in values if len(v) <= 48][:16]
            if 1 <= len(short_values) <= 16:
                attr_enums[attr] = short_values

    tag_attr_map = {
        tag: [a for a, _ in ctr.most_common()]
        for tag, ctr in tag_attrs.items()
    }

    tag_child_map = {
        tag: [c for c, _ in ctr.most_common()]
        for tag, ctr in tag_children.items()
    }

    # crude mandatory guesses
    mandatory_attrs = {}
    for tag, ctr in tag_attrs.items():
        total = tag_seen[tag]
        must = []
        for attr, count in ctr.items():
            if total > 0 and (count / total) >= 0.80:
                must.append(attr)
        mandatory_attrs[tag] = sorted(must)

    payload = {
        "SVG_TAGS": sorted(tag_seen.keys()),
        "TAG_TO_ATTRS": tag_attr_map,
        "TAG_TO_CHILDREN": tag_child_map,
        "MANDATORY_ATTRS": mandatory_attrs,
        "ATTR_TYPES": attr_types,
        "ATTR_ENUMS": attr_enums,
        "ATTR_SAMPLES": attr_samples,
        "PARSE_FAILURES": parse_failures,
    }

    with open(output_py, "w", encoding="utf-8") as f:
        f.write("# auto-generated by analyze_svg_corpus.py\n\n")
        for key in ["SVG_TAGS", "TAG_TO_ATTRS", "TAG_TO_CHILDREN", "MANDATORY_ATTRS", "ATTR_TYPES", "ATTR_ENUMS", "ATTR_SAMPLES", "PARSE_FAILURES"]:
            f.write(f"{key} = ")
            f.write(repr(payload[key]))
            f.write("\n\n")

    print(f"[+] Wrote metadata to {output_py}")
    print(f"[+] Parse failures: {parse_failures}")
    print(f"[+] Tags: {len(payload['SVG_TAGS'])}")
    print(f"[+] Attrs: {len(payload['ATTR_TYPES'])}")


if __name__ == "__main__":
    main()
