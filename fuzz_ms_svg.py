import zipfile
import shutil
import os
import tempfile
import subprocess
from pathlib import Path
import xml.etree.ElementTree as ET
import main

# === CONFIG ===
TEMPLATE_DOCX = "template.docx"
OUTPUT_DOCX   = "fuzzed.docx"
# SVG_MUTATOR   = ["python3", "main.py"]  # your mutator
BASE_SVG      = "seed.svg"
NUM_SVGS      = 10  # start small, increase later

WORD_MEDIA_DIR = "word/media"
RELS_FILE = "word/_rels/document.xml.rels"

# === UTIL ===

def unzip_docx(docx_path, extract_dir):
    with zipfile.ZipFile(docx_path, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)

def zip_docx(folder, output_path):
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as docx:
        for root, dirs, files in os.walk(folder):
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, folder)
                docx.write(full_path, rel_path)

def mutate_svg(seed_path, output_path):
    # subprocess.run(SVG_MUTATOR + [seed_path, output_path], check=True)
    fh = open(seed_path, "rb")
    data = fh.read()
    fh.close()

    # Now mutate...

    mutated = main.mutate_main(data)

    fh = open(output_path, "wb")
    fh.write(mutated)
    fh.close()
    return

def generate_svgs(media_dir):
    generated = []

    for i in range(NUM_SVGS):
        # out_svg = media_dir / f"fuzz{i}.svg"
        # image2.svg
        out_svg = media_dir / f"image2.svg"
        mutate_svg(BASE_SVG, str(out_svg))
        # generated.append(f"media/fuzz{i}.svg")
        generated.append(f"media/image2.svg")

    return generated

def update_relationships(rels_path, new_svgs):
    tree = ET.parse(rels_path)
    root = tree.getroot()

    # namespace fix
    ns = {"r": "http://schemas.openxmlformats.org/package/2006/relationships"}

    existing_ids = set()
    for rel in root.findall("r:Relationship", ns):
        existing_ids.add(rel.attrib["Id"])

    next_id = 1000  # avoid collisions

    for svg in new_svgs:
        rid = f"rId{next_id}"
        next_id += 1

        rel = ET.Element("Relationship")
        rel.set("Id", rid)
        rel.set("Type", "http://schemas.openxmlformats.org/officeDocument/2006/relationships/image")
        rel.set("Target", svg)

        root.append(rel)

    tree.write(rels_path, xml_declaration=True, encoding="UTF-8")

# === MAIN ===

def build_fuzzed_docx():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # 1. unzip
        unzip_docx(TEMPLATE_DOCX, tmpdir)

        media_dir = tmpdir / WORD_MEDIA_DIR
        rels_path = tmpdir / RELS_FILE

        # 2. generate mutated svgs
        new_svgs = generate_svgs(media_dir)

        # 3. update rels
        # update_relationships(rels_path, new_svgs)

        # 4. zip back
        zip_docx(tmpdir, OUTPUT_DOCX)

        print(f"[+] Generated {OUTPUT_DOCX}")

if __name__ == "__main__":
    build_fuzzed_docx()
