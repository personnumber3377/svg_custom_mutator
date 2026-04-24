import copy
import random
import string
import xml.etree.ElementTree as ET
import re

# Try to import generated metadata. If it does not exist, fallback.
# try:
import svg_auto_metadata as auto_meta
AUTO_SVG_TAGS = auto_meta.SVG_TAGS
AUTO_TAG_TO_ATTRS = auto_meta.TAG_TO_ATTRS
AUTO_TAG_TO_CHILDREN = auto_meta.TAG_TO_CHILDREN
AUTO_MANDATORY_ATTRS = auto_meta.MANDATORY_ATTRS
AUTO_ATTR_TYPES = auto_meta.ATTR_TYPES
AUTO_ATTR_ENUMS = auto_meta.ATTR_ENUMS
AUTO_ATTR_SAMPLES = auto_meta.ATTR_SAMPLES

MAX_NODES = 1000 # Maximum number of nodes to iterate over...

'''
except Exception:
    AUTO_SVG_TAGS = []
    AUTO_TAG_TO_ATTRS = {}
    AUTO_TAG_TO_CHILDREN = {}
    AUTO_MANDATORY_ATTRS = {}
    AUTO_ATTR_TYPES = {}
    AUTO_ATTR_ENUMS = {}
    AUTO_ATTR_SAMPLES = {}
'''

NS = "http://www.w3.org/2000/svg"
XLINK = "http://www.w3.org/1999/xlink"

ET.register_namespace("", NS)
ET.register_namespace("xlink", XLINK)

NUM_RE = re.compile(r"^[+-]?(?:\d+|\d*\.\d+)(?:[eE][+-]?\d+)?$")
URL_REF_RE = re.compile(r"^url\(#([^)]+)\)$")

COMMON_TAGS = [
    "svg", "g", "defs", "symbol", "use", "rect", "circle", "ellipse", "line",
    "path", "polygon", "polyline", "text", "tspan", "image",
    "linearGradient", "radialGradient", "stop", "pattern", "clipPath", "mask",
    "filter", "feGaussianBlur", "feOffset", "feBlend", "feColorMatrix",
    "feComponentTransfer", "feFuncR", "feFuncG", "feFuncB", "feFuncA",
    "feFlood", "feImage", "feTile", "feTurbulence", "feDisplacementMap",
    "feComposite", "feConvolveMatrix", "feMorphology",
    "feDiffuseLighting", "feSpecularLighting", "fePointLight",
    "feDistantLight", "feSpotLight", "feMerge", "feMergeNode"
]

SVG_TAGS = sorted(set(COMMON_TAGS + AUTO_SVG_TAGS))

PAINT_WORDS = [
    "none", "currentColor", "black", "white", "red", "green", "blue",
    "yellow", "purple", "orange", "pink", "gray", "lime"
]

ENUM_WORDS = [
    "userSpaceOnUse", "objectBoundingBox", "repeat", "reflect", "pad",
    "sRGB", "linearRGB", "butt", "round", "square", "miter", "bevel",
    "evenodd", "nonzero", "multiply", "screen", "darken", "lighten",
    "over", "atop", "arithmetic", "duplicate", "wrap", "none",
    "fractalNoise", "turbulence", "stitch", "noStitch",
    "matrix", "saturate", "hueRotate", "luminanceToAlpha",
    "discrete", "linear", "gamma", "identity",
    "visible", "hidden", "auto", "inherit", "initial",
    "xMinYMin", "xMidYMin", "xMaxYMin", "xMinYMid", "xMidYMid", "xMaxYMid",
    "xMinYMax", "xMidYMax", "xMaxYMax", "meet", "slice",
]

TRANSFORM_FUNCS = ["matrix", "translate", "scale", "rotate", "skewX", "skewY"]
PATH_CMDS = "MmLlHhVvCcSsQqTtAaZz"

DEFAULT_TAG_TO_ATTRS = {
    "svg": ["viewBox", "width", "height", "x", "y", "preserveAspectRatio"],
    "g": ["id", "class", "transform", "opacity", "style"],
    "rect": ["x", "y", "width", "height", "rx", "ry", "fill", "stroke", "stroke-width", "filter", "transform"],
    "circle": ["cx", "cy", "r", "fill", "stroke", "stroke-width", "filter", "transform"],
    "ellipse": ["cx", "cy", "rx", "ry", "fill", "stroke", "stroke-width", "filter", "transform"],
    "line": ["x1", "y1", "x2", "y2", "stroke", "stroke-width", "transform"],
    "path": ["d", "fill", "stroke", "stroke-width", "filter", "transform"],
    "polygon": ["points", "fill", "stroke", "stroke-width", "filter", "transform"],
    "polyline": ["points", "fill", "stroke", "stroke-width", "filter", "transform"],
    "text": ["x", "y", "fill", "font-size", "font-family", "transform", "textLength", "lengthAdjust"],
    "tspan": ["x", "y", "dx", "dy", "fill"],
    "image": ["x", "y", "width", "height", "href", "xlink:href"],
    "use": ["href", "xlink:href", "x", "y", "width", "height"],
    "defs": [],
    "symbol": ["id", "viewBox", "width", "height"],
    "linearGradient": ["id", "x1", "y1", "x2", "y2", "gradientUnits", "gradientTransform", "spreadMethod", "href", "xlink:href"],
    "radialGradient": ["id", "cx", "cy", "r", "fx", "fy", "gradientUnits", "gradientTransform", "spreadMethod", "href", "xlink:href"],
    "stop": ["offset", "stop-color", "stop-opacity"],
    "pattern": ["id", "x", "y", "width", "height", "patternUnits", "patternContentUnits", "patternTransform", "viewBox"],
    "clipPath": ["id", "clipPathUnits"],
    "mask": ["id", "x", "y", "width", "height", "maskUnits", "maskContentUnits"],
    "filter": ["id", "x", "y", "width", "height", "filterUnits", "primitiveUnits"],
    "feGaussianBlur": ["in", "stdDeviation", "result"],
    "feOffset": ["in", "dx", "dy", "result"],
    "feBlend": ["in", "in2", "mode", "result"],
    "feColorMatrix": ["in", "type", "values", "result"],
    "feComponentTransfer": ["in", "result"],
    "feFuncR": ["type", "tableValues", "slope", "intercept", "amplitude", "exponent", "offset"],
    "feFuncG": ["type", "tableValues", "slope", "intercept", "amplitude", "exponent", "offset"],
    "feFuncB": ["type", "tableValues", "slope", "intercept", "amplitude", "exponent", "offset"],
    "feFuncA": ["type", "tableValues", "slope", "intercept", "amplitude", "exponent", "offset"],
    "feFlood": ["flood-color", "flood-opacity", "result"],
    "feImage": ["href", "xlink:href", "result"],
    "feTile": ["in", "result"],
    "feTurbulence": ["baseFrequency", "numOctaves", "seed", "stitchTiles", "type", "result"],
    "feDisplacementMap": ["in", "in2", "scale", "xChannelSelector", "yChannelSelector", "result"],
    "feComposite": ["in", "in2", "operator", "k1", "k2", "k3", "k4", "result"],
    "feConvolveMatrix": ["in", "order", "kernelMatrix", "divisor", "bias", "targetX", "targetY", "edgeMode", "kernelUnitLength", "preserveAlpha", "result"],
    "feMorphology": ["in", "operator", "radius", "result"],
    "feDiffuseLighting": ["in", "surfaceScale", "diffuseConstant", "lighting-color", "result"],
    "feSpecularLighting": ["in", "surfaceScale", "specularConstant", "specularExponent", "lighting-color", "result"],
    "fePointLight": ["x", "y", "z"],
    "feDistantLight": ["azimuth", "elevation"],
    "feSpotLight": ["x", "y", "z", "pointsAtX", "pointsAtY", "pointsAtZ", "specularExponent", "limitingConeAngle"],
    "feMerge": ["result"],
    "feMergeNode": ["in"],
}

DEFAULT_TAG_TO_CHILDREN = {
    "svg": ["defs", "g", "rect", "circle", "ellipse", "line", "path", "polygon", "polyline", "text", "image", "use", "filter", "pattern", "linearGradient", "radialGradient"],
    "g": ["g", "rect", "circle", "ellipse", "line", "path", "polygon", "polyline", "text", "image", "use"],
    "defs": ["filter", "pattern", "linearGradient", "radialGradient", "clipPath", "mask", "symbol"],
    "linearGradient": ["stop"],
    "radialGradient": ["stop"],
    "pattern": ["rect", "circle", "ellipse", "line", "path", "polygon", "polyline", "text", "image", "use", "g"],
    "clipPath": ["rect", "circle", "ellipse", "line", "path", "polygon", "polyline", "text", "use"],
    "mask": ["rect", "circle", "ellipse", "line", "path", "polygon", "polyline", "text", "use", "g"],
    "filter": [
        "feGaussianBlur", "feOffset", "feBlend", "feColorMatrix", "feComponentTransfer",
        "feFlood", "feImage", "feTile", "feTurbulence", "feDisplacementMap",
        "feComposite", "feConvolveMatrix", "feMorphology", "feDiffuseLighting",
        "feSpecularLighting", "feMerge"
    ],
    "feComponentTransfer": ["feFuncR", "feFuncG", "feFuncB", "feFuncA"],
    "feDiffuseLighting": ["fePointLight", "feDistantLight", "feSpotLight"],
    "feSpecularLighting": ["fePointLight", "feDistantLight", "feSpotLight"],
    "feMerge": ["feMergeNode"],
    "symbol": ["g", "rect", "circle", "ellipse", "line", "path", "polygon", "polyline", "text", "image", "use"],
}

TAG_TO_ATTRS = dict(DEFAULT_TAG_TO_ATTRS)
for k, v in AUTO_TAG_TO_ATTRS.items():
    TAG_TO_ATTRS[k] = list(dict.fromkeys(TAG_TO_ATTRS.get(k, []) + v))

TAG_TO_CHILDREN = dict(DEFAULT_TAG_TO_CHILDREN)
for k, v in AUTO_TAG_TO_CHILDREN.items():
    TAG_TO_CHILDREN[k] = list(dict.fromkeys(TAG_TO_CHILDREN.get(k, []) + v))

MANDATORY_ATTRS = dict(AUTO_MANDATORY_ATTRS)
ATTR_TYPES = dict(AUTO_ATTR_TYPES)
ATTR_ENUMS = dict(AUTO_ATTR_ENUMS)
ATTR_SAMPLES = dict(AUTO_ATTR_SAMPLES)

for attr in [
    "gradientUnits", "patternUnits", "patternContentUnits", "filterUnits", "primitiveUnits", "clipPathUnits", "maskUnits", "maskContentUnits"
]:
    ATTR_TYPES.setdefault(attr, "enum")
    ATTR_ENUMS.setdefault(attr, ["userSpaceOnUse", "objectBoundingBox"])

for attr, vals in {
    "spreadMethod": ["pad", "reflect", "repeat"],
    "mode": ["normal", "multiply", "screen", "darken", "lighten"],
    "operator": ["over", "in", "out", "atop", "xor", "arithmetic"],
    "edgeMode": ["duplicate", "wrap", "none"],
    "stitchTiles": ["stitch", "noStitch"],
    "type": ["matrix", "saturate", "hueRotate", "luminanceToAlpha", "identity", "table", "discrete", "linear", "gamma", "fractalNoise", "turbulence"],
    "xChannelSelector": ["R", "G", "B", "A"],
    "yChannelSelector": ["R", "G", "B", "A"],
    "preserveAlpha": ["true", "false"],
    "preserveAspectRatio": [
        "none", "xMinYMin meet", "xMidYMid meet", "xMaxYMax meet",
        "xMinYMin slice", "xMidYMid slice", "xMaxYMax slice"
    ],
}.items():
    ATTR_TYPES.setdefault(attr, "enum")
    ATTR_ENUMS.setdefault(attr, vals)

IDREF_ATTRS = {"href", "xlink:href", "filter", "clip-path", "mask", "marker-start", "marker-mid", "marker-end", "fill", "stroke"}

# Generic string mutator...
def mutate_string(s: str) -> str:
    if not s:
        return random.choice(string.printable) * 1000

    s = list(s)
    ops = ["flip", "insert", "delete", "dup", "swap", "num", "token"]
    op = random.choice(ops)

    i = random.randrange(len(s))

    if op == "flip":
        # flip one character
        s[i] = chr(random.randrange(32, 127))

    elif op == "insert":
        # insert random substring
        insert = "".join(random.choice(string.printable) for _ in range(random.randint(1, 8)))
        s.insert(i, insert)

    elif op == "delete":
        # delete a chunk
        del s[i:i + random.randint(1, 4)]

    elif op == "dup":
        # duplicate a slice
        j = random.randrange(len(s))
        if i < j:
            s[i:j] = s[i:j] * 2

    elif op == "swap":
        # swap two chars
        j = random.randrange(len(s))
        s[i], s[j] = s[j], s[i]

    elif op == "num":
        # replace with extreme number
        s[i] = random.choice(["0", "-1", "1e309", "-1e309", "999999999999999999999"])

    elif op == "token":
        # inject interesting tokens
        tokens = ["<svg>", "</svg>", "url(#id)", "NaN", "Infinity", "%s", "../../"]
        s.insert(i, random.choice(tokens))

    return "".join(s)

def qname(tag: str) -> str:
    return f"{{{NS}}}{tag}"

def strip_ns(tag: str) -> str:
    if "}" in tag:
        return tag.split("}", 1)[1]
    return tag

def rand_id() -> str:
    return "id" + str(random.randrange(1_000_000_000))

def rand_int(a=-10000, b=10000) -> str:
    return str(random.randint(a, b))

def rand_float(a=-10000.0, b=10000.0) -> str:
    return f"{random.uniform(a, b):.6g}"

def rand_num() -> str:
    if random.random() < 0.4:
        return rand_int()
    return rand_float()

def rand_percent() -> str:
    return f"{random.uniform(-200, 200):.6g}%"

def rand_lenish() -> str:
    if random.random() < 0.2:
        return rand_percent()
    return rand_num()

def rand_color() -> str:
    if random.random() < 0.45:
        return random.choice(PAINT_WORDS)
    if random.random() < 0.5:
        return f"rgb({random.randint(0,255)},{random.randint(0,255)},{random.randint(0,255)})"
    return "#" + "".join(random.choice("0123456789ABCDEF") for _ in range(random.choice([3, 6, 8])))

def rand_transform() -> str:
    parts = []
    for _ in range(random.randint(1, 5)):
        f = random.choice(TRANSFORM_FUNCS)
        if f == "matrix":
            args = [rand_num() for _ in range(6)]
        elif f == "translate":
            args = [rand_num() for _ in range(random.choice([1,2]))]
        elif f == "scale":
            args = [rand_num() for _ in range(random.choice([1,2]))]
        elif f == "rotate":
            args = [rand_num() for _ in range(random.choice([1,3]))]
        else:
            args = [rand_num()]
        parts.append(f + "(" + " ".join(args) + ")")
    return " ".join(parts)

def rand_path() -> str:
    out = []
    for _ in range(random.randint(1, 1000)): # Make really long paths as default...
        cmd = random.choice(PATH_CMDS)
        argc = {
            "M":2,"m":2,"L":2,"l":2,"H":1,"h":1,"V":1,"v":1,
            "C":6,"c":6,"S":4,"s":4,"Q":4,"q":4,"T":2,"t":2,
            "A":7,"a":7,"Z":0,"z":0
        }[cmd]
        if argc == 0:
            out.append(cmd)
        else:
            vals = []
            for i in range(argc):
                if cmd in "Aa" and i in {3,4}:
                    vals.append(random.choice(["0","1"]))
                else:
                    vals.append(rand_num())
            out.append(cmd + " " + " ".join(vals))
    return " ".join(out)

def rand_points() -> str:
    return " ".join(f"{rand_num()},{rand_num()}" for _ in range(random.randint(2, 20)))

def rand_viewbox() -> str:
    return " ".join([rand_num(), rand_num(), rand_num(), rand_num()])

def rand_table_values() -> str:
    return " ".join(rand_num() for _ in range(random.randint(1, 12)))

def rand_kernel_matrix() -> str:
    n = random.choice([1, 2, 3, 4, 5, 9])
    return " ".join(rand_num() for _ in range(n))

def rand_style() -> str:
    props = []
    candidates = ["fill", "stroke", "stroke-width", "opacity", "font-size", "filter", "transform"]
    for _ in range(random.randint(1, 5)):
        p = random.choice(candidates)
        if p in {"fill", "stroke"}:
            v = rand_color()
        elif p == "stroke-width":
            v = rand_num()
        elif p == "opacity":
            v = rand_float(0, 2)
        elif p == "font-size":
            v = rand_lenish()
        elif p == "filter":
            v = "none"
        elif p == "transform":
            v = rand_transform()
        else:
            v = "".join(random.choice(string.ascii_letters) for _ in range(random.randint(1, 10)))
        props.append(f"{p}:{v}")
    return ";".join(props) + ";"

def random_text(original_text: str) -> str:
    if random.random() < 0.80: # 80 percent chance to just mutate the string...
        mut_string = mutate_string(original_text)
        print(mut_string)
        return mut_string
    choices = [
        "hello", "text", "svg", "filter", "pattern", "A", "😀", "مرحبا",
        "こんにちは", "specular", "convolve", "matrix", "".join(random.choice(string.printable) for _ in range(random.randint(0, 3000)))
    ]
    return random.choice(choices)

def collect_ids(root):
    ids = []
    for i, e in enumerate(root.iter()):
        if i >= MAX_NODES:
            break
        if "id" in e.attrib:
            ids.append(e.attrib["id"])
    return ids

# This is to avoid slowing down due to unbounded iteration of the elements in the tree...
def count_nodes(root, max_nodes=MAX_NODES):
    count = 0
    for _ in root.iter():
        count += 1
        if count > max_nodes:
            print("[!] Node limit exceeded")
            return count
    return count
'''
def all_nodes(root):
    print(ET.tostring(root))
    return list(root.iter())
'''

def all_nodes(root, max_nodes=MAX_NODES):
    nodes = []
    for i, node in enumerate(root.iter()):
        if i >= max_nodes:
            print("[!] all_nodes truncated at", max_nodes)
            break
        nodes.append(node)
    return nodes

def find_parent(root, target):
    for i, p in enumerate(root.iter()):
        if i >= MAX_NODES:
            break
        for c in list(p):
            if c is target:
                return p
    return None

def pick_existing_id(context):
    if context["ids"]:
        return random.choice(context["ids"])
    new = rand_id()
    context["ids"].append(new)
    return new

def make_url_ref(context):
    return f"url(#{pick_existing_id(context)})"

def make_href_ref(context):
    return f"#{pick_existing_id(context)}"

def guess_attr_type(attr: str) -> str:
    if attr in ATTR_TYPES:
        return ATTR_TYPES[attr]
    low = attr.lower()
    if low in {"x","y","x1","y1","x2","y2","cx","cy","r","rx","ry","width","height","dx","dy","opacity","offset","scale","radius","surfaceScale","specularConstant","specularExponent","diffuseConstant","azimuth","elevation","limitingConeAngle","seed","numOctaves","bias","divisor","targetX","targetY","k1","k2","k3","k4"}:
        return "number"
    if low in {"d"}:
        return "path"
    if low in {"points"}:
        return "points"
    if low in {"transform","gradientTransform","patternTransform"}:
        return "transform"
    if low in {"viewBox"}:
        return "viewbox"
    if low in {"fill","stroke","flood-color","lighting-color","stop-color","color"}:
        return "paint"
    if low in {"href","xlink:href"}:
        return "href"
    if low in {"filter","clip-path","mask","marker-start","marker-mid","marker-end"}:
        return "url_ref"
    if low == "id":
        return "id"
    if low == "style":
        return "style"
    return "string"

def generate_attr_value(attr: str, context, tag: str = None) -> str:
    atype = guess_attr_type(attr)

    if atype == "enum":
        vals = ATTR_ENUMS.get(attr, ENUM_WORDS)
        return random.choice(vals)
    if atype == "integer":
        return rand_int()
    if atype == "number":
        if attr in {"width", "height", "r", "rx", "ry", "stroke-width", "stdDeviation", "radius"}:
            return rand_float(0, 1000)
        if attr == "offset":
            return random.choice([rand_percent(), rand_float(0, 1)])
        return rand_num()
    if atype == "paint":
        if attr in {"fill", "stroke"} and random.random() < 0.2:
            return make_url_ref(context)
        return rand_color()
    if atype == "path":
        return rand_path()
    if atype == "points":
        return rand_points()
    if atype == "transform":
        return rand_transform()
    if atype == "viewbox":
        return rand_viewbox()
    if atype == "id":
        new = rand_id()
        context["ids"].append(new)
        return new
    if atype == "href":
        if random.random() < 0.8:
            return make_href_ref(context)
        return random.choice([
            "data:image/png;base64,AAAA",
            "data:image/jpeg;base64,AAAA",
            "#"+pick_existing_id(context)
        ])
    if atype == "url_ref":
        return make_url_ref(context)
    if atype == "style":
        return rand_style()
    if attr == "kernelMatrix":
        return rand_kernel_matrix()
    if attr == "tableValues":
        return rand_table_values()
    if attr == "baseFrequency":
        return random.choice([rand_num(), rand_num()+" "+rand_num()])
    if attr == "order":
        return random.choice([str(random.randint(1, 7)), f"{random.randint(1,7)} {random.randint(1,7)}"])
    if attr == "kernelUnitLength":
        return random.choice([rand_num(), rand_num()+" "+rand_num()])
    if attr == "values":
        return " ".join(rand_num() for _ in range(random.randint(1, 20)))

    enum_candidates = ATTR_ENUMS.get(attr)
    if enum_candidates and random.random() < 0.6:
        return random.choice(enum_candidates)

    samples = ATTR_SAMPLES.get(attr)
    if samples and random.random() < 0.3:
        return random.choice(samples)

    return random.choice([
        rand_num(), rand_color(), rand_transform(),
        "".join(random.choice(string.ascii_letters + string.digits + "-_:") for _ in range(random.randint(0, 24))),
        random.choice(ENUM_WORDS)
    ])

def set_required_attrs(elem, tag, context):
    attrs = TAG_TO_ATTRS.get(tag, [])
    mandatory = AUTO_MANDATORY_ATTRS.get(tag, [])

    must = set(mandatory)

    # Add some hard-coded practical requirements
    if tag == "svg":
        must.update(["viewBox"])
    elif tag == "rect":
        must.update(["x", "y", "width", "height"])
    elif tag == "circle":
        must.update(["cx", "cy", "r"])
    elif tag == "ellipse":
        must.update(["cx", "cy", "rx", "ry"])
    elif tag == "line":
        must.update(["x1", "y1", "x2", "y2"])
    elif tag == "path":
        must.update(["d"])
    elif tag in {"polygon", "polyline"}:
        must.update(["points"])
    elif tag in {"linearGradient", "radialGradient", "pattern", "clipPath", "mask", "filter", "symbol"}:
        must.update(["id"])
    elif tag == "stop":
        must.update(["offset"])
    elif tag == "image":
        must.update(["x", "y", "width", "height"])
    elif tag == "use":
        must.update(["href"])
    elif tag == "feGaussianBlur":
        must.update(["stdDeviation"])
    elif tag == "feOffset":
        must.update(["dx", "dy"])
    elif tag == "feColorMatrix":
        must.update(["type"])
    elif tag == "feBlend":
        must.update(["mode"])
    elif tag == "feComponentTransfer":
        pass
    elif tag in {"feFuncR", "feFuncG", "feFuncB", "feFuncA"}:
        must.update(["type"])
    elif tag == "feTurbulence":
        must.update(["type", "baseFrequency"])
    elif tag == "feDisplacementMap":
        must.update(["scale"])
    elif tag == "feComposite":
        must.update(["operator"])
    elif tag == "feConvolveMatrix":
        must.update(["order", "kernelMatrix"])
    elif tag == "feMorphology":
        must.update(["operator", "radius"])
    elif tag == "feDiffuseLighting":
        must.update(["surfaceScale", "diffuseConstant"])
    elif tag == "feSpecularLighting":
        must.update(["surfaceScale", "specularConstant", "specularExponent"])
    elif tag == "fePointLight":
        must.update(["x", "y", "z"])
    elif tag == "feDistantLight":
        must.update(["azimuth", "elevation"])
    elif tag == "feSpotLight":
        must.update(["x", "y", "z", "pointsAtX", "pointsAtY", "pointsAtZ"])

    for a in must:
        if a not in elem.attrib:
            elem.attrib[a] = generate_attr_value(a, context, tag)

    # sprinkle more attrs
    pool = list(attrs)
    random.shuffle(pool)
    for a in pool[:random.randint(0, min(6, len(pool)))]:
        if a not in elem.attrib:
            elem.attrib[a] = generate_attr_value(a, context, tag)

def build_node_from_scratch(tag: str, context):
    elem = ET.Element(qname(tag))
    set_required_attrs(elem, tag, context)

    if tag in {"text", "tspan"}:
        elem.text = random_text(elem.text)

    if tag in {"linearGradient", "radialGradient"}:
        for _ in range(random.randint(1, 5)):
            stop = ET.Element(qname("stop"))
            set_required_attrs(stop, "stop", context)
            if "stop-color" not in stop.attrib:
                stop.attrib["stop-color"] = rand_color()
            elem.append(stop)

    elif tag == "feComponentTransfer":
        subchoices = ["feFuncR", "feFuncG", "feFuncB", "feFuncA"]
        random.shuffle(subchoices)
        for sub in subchoices[:random.randint(1, 4)]:
            child = ET.Element(qname(sub))
            set_required_attrs(child, sub, context)
            elem.append(child)

    elif tag in {"feDiffuseLighting", "feSpecularLighting"}:
        sub = random.choice(["fePointLight", "feDistantLight", "feSpotLight"])
        child = ET.Element(qname(sub))
        set_required_attrs(child, sub, context)
        elem.append(child)

    elif tag == "feMerge":
        for _ in range(random.randint(1, 4)):
            child = ET.Element(qname("feMergeNode"))
            set_required_attrs(child, "feMergeNode", context)
            if random.random() < 0.7:
                child.attrib["in"] = random.choice(["SourceGraphic", "SourceAlpha", "BackgroundImage", "BackgroundAlpha", "FillPaint", "StrokePaint"])
            elem.append(child)

    elif tag == "pattern":
        for _ in range(random.randint(1, 4)):
            child_tag = random.choice(["rect", "circle", "ellipse", "path", "line", "polygon", "polyline", "text", "g"])
            elem.append(build_node_from_scratch(child_tag, context))

    elif tag in {"svg", "g", "defs", "symbol", "clipPath", "mask"}:
        child_pool = TAG_TO_CHILDREN.get(tag, [])
        for _ in range(random.randint(0, min(5, max(1, len(child_pool))))):
            ctag = random.choice(child_pool) if child_pool else random.choice(SVG_TAGS)
            elem.append(build_node_from_scratch(ctag, context))

    return elem

def build_filter_subtree(context):
    filt = build_node_from_scratch("filter", context)

    recipe = random.choice([
        ["feGaussianBlur"],
        ["feOffset"],
        ["feGaussianBlur", "feOffset", "feBlend"],
        ["feColorMatrix"],
        ["feComponentTransfer"],
        ["feTurbulence", "feDisplacementMap"],
        ["feConvolveMatrix"],
        ["feMorphology"],
        ["feFlood", "feBlend"],
        ["feSpecularLighting"],
        ["feDiffuseLighting"],
        ["feImage", "feTile"],
        ["feComposite"],
        ["feMerge"],
        ["feGaussianBlur", "feColorMatrix", "feBlend"],
    ])

    prev_result = "SourceGraphic"
    for i, tag in enumerate(recipe):
        child = build_node_from_scratch(tag, context)
        if "in" in TAG_TO_ATTRS.get(tag, []) or tag.startswith("fe"):
            if tag not in {"fePointLight", "feDistantLight", "feSpotLight", "feFuncR", "feFuncG", "feFuncB", "feFuncA", "feMergeNode"}:
                child.attrib["in"] = prev_result
        if "in2" in TAG_TO_ATTRS.get(tag, []):
            child.attrib["in2"] = random.choice(["SourceGraphic", "SourceAlpha", prev_result, "BackgroundImage", "FillPaint", "StrokePaint"])
        if tag != recipe[-1] and "result" not in child.attrib:
            child.attrib["result"] = "res" + str(i)
            prev_result = child.attrib["result"]
        filt.append(child)

    return filt

def mutate_existing_attr(elem, context):
    if not elem.attrib:
        return False
    k = random.choice(list(elem.attrib.keys()))
    elem.attrib[k] = generate_attr_value(k, context, strip_ns(elem.tag))
    return True

def add_attr(elem, context):
    tag = strip_ns(elem.tag)
    pool = TAG_TO_ATTRS.get(tag, []) or list(ATTR_TYPES.keys()) or ["x", "y", "fill", "stroke", "transform", "d"]
    k = random.choice(pool)
    elem.attrib[k] = generate_attr_value(k, context, tag)

def remove_attr(elem):
    if not elem.attrib:
        return False
    k = random.choice(list(elem.attrib.keys()))
    del elem.attrib[k]
    return True

def duplicate_node(root, elem):
    target = random.choice(all_nodes(root))
    target.append(copy.deepcopy(elem))

def reparent_node(root, elem):
    parent = find_parent(root, elem)
    if parent is None:
        return
    target = random.choice(all_nodes(root))
    if target is elem:
        return
    try:
        parent.remove(elem)
        target.append(elem)
    except Exception:
        pass

def remove_node(root, elem):
    parent = find_parent(root, elem)
    if parent is not None:
        try:
            parent.remove(elem)
        except Exception:
            pass

def inject_scratch_node(root, context):
    target = random.choice(all_nodes(root))
    tag = random.choice(SVG_TAGS)
    node = build_node_from_scratch(tag, context)
    target.append(node)

def inject_filter_system(root, context):
    nodes = all_nodes(root)
    defs_nodes = [n for n in nodes if strip_ns(n.tag) == "defs"]
    if defs_nodes:
        defs = random.choice(defs_nodes)
    else:
        defs = ET.Element(qname("defs"))
        root.insert(0, defs)

    filt = build_filter_subtree(context)
    defs.append(filt)

    # attach the filter to some drawable node
    drawables = [n for n in all_nodes(root) if strip_ns(n.tag) in {"rect", "circle", "ellipse", "line", "path", "polygon", "polyline", "text", "image", "g"}]
    if drawables and "id" in filt.attrib:
        random.choice(drawables).attrib["filter"] = f"url(#{filt.attrib['id']})"

def inject_gradient_system(root, context):
    defs_nodes = [n for n in all_nodes(root) if strip_ns(n.tag) == "defs"]
    defs = random.choice(defs_nodes) if defs_nodes else ET.Element(qname("defs"))
    if defs not in list(root):
        root.insert(0, defs)

    grad_tag = random.choice(["linearGradient", "radialGradient"])
    grad = build_node_from_scratch(grad_tag, context)
    defs.append(grad)

    drawables = [n for n in all_nodes(root) if strip_ns(n.tag) in {"rect", "circle", "ellipse", "path", "polygon", "polyline", "text"}]
    if drawables and "id" in grad.attrib:
        random.choice(drawables).attrib[random.choice(["fill", "stroke"])] = f"url(#{grad.attrib['id']})"

def inject_pattern_system(root, context):
    defs_nodes = [n for n in all_nodes(root) if strip_ns(n.tag) == "defs"]
    defs = random.choice(defs_nodes) if defs_nodes else ET.Element(qname("defs"))
    if defs not in list(root):
        root.insert(0, defs)

    pattern = build_node_from_scratch("pattern", context)
    defs.append(pattern)

    drawables = [n for n in all_nodes(root) if strip_ns(n.tag) in {"rect", "circle", "ellipse", "path", "polygon", "polyline", "text"}]
    if drawables and "id" in pattern.attrib:
        random.choice(drawables).attrib["fill"] = f"url(#{pattern.attrib['id']})"

def mutate_text(elem):
    if elem.text is None:
        elem.text = random_text(elem.text)
    else:
        s = elem.text
        if not s:
            elem.text = random_text(elem.text)
            return
        mode = random.randrange(4)
        if mode == 0 and len(s) > 0:
            i = random.randrange(len(s))
            elem.text = s[:i] + random.choice(string.printable) + s[i+1:]
        elif mode == 1:
            elem.text += random_text(elem.text)
        elif mode == 2:
            elem.text = random_text(elem.text)
        else:
            elem.text = ""

def repair_references(root, context):
    ids = collect_ids(root)
    context["ids"] = ids[:]

    if not ids:
        # create an id somewhere
        nodes = [n for n in all_nodes(root) if strip_ns(n.tag) in {"filter", "pattern", "linearGradient", "radialGradient", "clipPath", "mask", "symbol", "path"}]
        if nodes:
            n = random.choice(nodes)
            n.attrib["id"] = rand_id()
            ids = collect_ids(root)
            context["ids"] = ids[:]

    for elem in all_nodes(root):
        for attr, val in list(elem.attrib.items()):
            if attr in IDREF_ATTRS:
                if attr in {"href", "xlink:href"}:
                    if random.random() < 0.6:
                        elem.attrib[attr] = make_href_ref(context)
                else:
                    if random.random() < 0.6:
                        elem.attrib[attr] = make_url_ref(context)

def ensure_root(root, context):
    if strip_ns(root.tag) != "svg":
        newroot = ET.Element(qname("svg"))
        set_required_attrs(newroot, "svg", context)
        newroot.append(root)
        return newroot
    set_required_attrs(root, "svg", context)
    return root

def single_mutation(root, context):
    ops = [
        "mut_attr", "add_attr", "del_attr", "dup_node", "reparent", "remove",
        "inject_node", "inject_filter", "inject_gradient", "inject_pattern",
        "mut_text", "repair_refs"
    ]
    op = random.choice(ops)
    nodes = all_nodes(root)
    elem = random.choice(nodes)

    if op == "mut_attr":
        mutate_existing_attr(elem, context)
    elif op == "add_attr":
        add_attr(elem, context)
    elif op == "del_attr":
        remove_attr(elem)
    elif op == "dup_node":
        duplicate_node(root, elem)
    elif op == "reparent":
        reparent_node(root, elem)
    elif op == "remove":
        remove_node(root, elem)
    elif op == "inject_node":
        inject_scratch_node(root, context)
    elif op == "inject_filter":
        inject_filter_system(root, context)
    elif op == "inject_gradient":
        inject_gradient_system(root, context)
    elif op == "inject_pattern":
        inject_pattern_system(root, context)
    elif op == "mut_text":
        mutate_text(elem)
    elif op == "repair_refs":
        repair_references(root, context)

# This is because of the shit...
def safe_tostring(root, max_nodes=MAX_NODES):
    count = 0
    for _ in root.iter():
        count += 1
        if count > max_nodes:
            print("[!] Too many nodes, skipping serialization")
            return None

    return ET.tostring(root, encoding="utf-8", short_empty_elements=True)

def mutate_main(in_bytes: bytes) -> bytes:
    try:
        s = in_bytes.decode("utf-8", errors="ignore")
        root = ET.fromstring(s)
    except Exception:
        # if parsing fails, sometimes just generate from scratch
        context = {"ids": []}
        root = build_node_from_scratch("svg", context)

    context = {"ids": collect_ids(root)}
    root = ensure_root(root, context)

    for _ in range(random.randint(2, 10)):
        single_mutation(root, context)

    # occasionally graft an entirely new subsystem
    if random.random() < 0.2:
        inject_filter_system(root, context)
    if random.random() < 0.15:
        inject_gradient_system(root, context)
    if random.random() < 0.15:
        inject_pattern_system(root, context)

    repair_references(root, context)

    # out = ET.tostring(root, encoding="utf-8", short_empty_elements=True)

    out = safe_tostring(root)
    if out is None:
        return in_bytes

    # scrub namespace pollution from ElementTree
    out = out.replace(b"</ns0:", b"</")
    out = out.replace(b"<ns0:", b"<")
    out = out.replace(b":ns0", b"")
    out = out.replace(b"ns1:href", b"xlink:href")

    return out


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} in.svg out.svg")
        raise SystemExit(1)

    with open(sys.argv[1], "rb") as f:
        data = f.read()

    out = mutate_main(data)

    with open(sys.argv[2], "wb") as f:
        f.write(out)

    print("[+] Wrote mutated SVG")