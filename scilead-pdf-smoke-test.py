"""Local diagnostic fixture only: this is NOT a SciLead paper reproduction."""
import json
import os
from pathlib import Path
import subprocess
import sys
import textwrap
import time

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "smoke"
OUT.mkdir(exist_ok=True)
os.chdir(OUT)  # Chroma's default Settings must not discover an unrelated .env.
RETRIEVAL_ONLY = "--retrieval-only" in sys.argv
POPPLER = ROOT / "tools/pdf-system/Library/bin"
TESSERACT = ROOT / "tools/tesseract"
os.environ.update({
    "HF_HOME": str(ROOT / "assets/huggingface"),
    "HF_HUB_OFFLINE": "1", "TRANSFORMERS_OFFLINE": "1",
    "HF_HUB_DISABLE_TELEMETRY": "1", "HF_HUB_DISABLE_IMPLICIT_TOKEN": "1",
    "HF_TOKEN": "", "HUGGING_FACE_HUB_TOKEN": "",
    "NLTK_DATA": str(ROOT / "assets/nltk_data"),
    "TESSDATA_PREFIX": str(TESSERACT / "tessdata"),
    "ANONYMIZED_TELEMETRY": "False", "DO_NOT_TRACK": "1",
    "LANGCHAIN_TRACING": "false", "LANGCHAIN_TRACING_V2": "false",
    "LANGSMITH_TRACING": "false",
    "MPLCONFIGDIR": str(ROOT / "assets/matplotlib-cache"),
})
os.environ["PATH"] = str(TESSERACT) + os.pathsep + str(POPPLER) + os.pathsep + os.environ.get("PATH", "")


def guard(event, args):
    if event in ("socket.connect", "socket.getaddrinfo"):
        raise RuntimeError("Offline diagnostic prohibits network access")
    if event == "open" and isinstance(args[0], (str, bytes)):
        p = os.fsdecode(args[0]).replace("\\", "/").lower()
        if Path(p).name.startswith(".env") or "/.codex/" in p or "/.aws/" in p:
            raise RuntimeError("Sensitive configuration access prohibited")


sys.addaudithook(guard)
results = {"kind": "synthetic environment diagnostic; NOT a SciLead paper", "checks": {}}
if RETRIEVAL_ONLY:
    results = json.loads((OUT / "diagnostic-results.json").read_text(encoding="utf-8"))


def save():
    (OUT / "diagnostic-results.json").write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")


def check(name, fn):
    start = time.monotonic()
    try:
        data = fn()
        results["checks"][name] = {"status": "PASS", "seconds": round(time.monotonic() - start, 2), "detail": data}
    except Exception as exc:
        import traceback
        traceback.print_exc()
        results["checks"][name] = {"status": "FAIL", "seconds": round(time.monotonic() - start, 2), "error": str(exc), "type": type(exc).__name__}
    print(name, json.dumps(results["checks"][name]), flush=True)
    save()


def make_fixture():
    from pypdf import PdfWriter
    from pypdf.generic import NameObject, DictionaryObject, DecodedStreamObject
    writer = PdfWriter()
    page = writer.add_blank_page(width=612, height=792)
    fonts = DictionaryObject()
    for name, face in [("F1", "Times-Roman"), ("F2", "Times-Bold")]:
        font = DictionaryObject({NameObject("/Type"): NameObject("/Font"), NameObject("/Subtype"): NameObject("/Type1"), NameObject("/BaseFont"): NameObject("/" + face)})
        fonts[NameObject("/" + name)] = writer._add_object(font)
    page[NameObject("/Resources")] = DictionaryObject({NameObject("/Font"): fonts})
    commands = []
    def text(x, y, value, size=11, font="F1"):
        value = value.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        commands.append(f"BT /{font} {size} Tf {x} {y} Td ({value}) Tj ET")
    text(54, 742, "SCILEAD Environment Diagnostic", 20, "F2")
    text(54, 720, "Synthetic fixture - not an actual SciLead paper or experimental result", 10)
    text(54, 681, "1. Test description", 14, "F2")
    paragraph = "This locally generated page validates PDF rendering, English optical character recognition, document layout detection and table structure recognition. All model names, datasets and scores below are synthetic diagnostic values. They are not research findings. No paper reproduction or extraction accuracy is claimed."
    for i, line in enumerate(textwrap.wrap(paragraph, width=96)):
        text(54, 657 - 15 * i, line)
    text(54, 555, "2. Synthetic benchmark results", 14, "F2")
    text(54, 529, "Table 1: Synthetic results for an environment smoke test.", 11)
    columns = [58, 218, 350, 445]
    rows = [["Model", "Dataset", "Metric", "Score"],
            ["Synthetic Baseline A", "Synthetic QA", "F1", "84.2"],
            ["Synthetic Baseline B", "Synthetic QA", "F1", "87.6"],
            ["Synthetic Model C", "Synthetic QA", "F1", "90.1"],
            ["Synthetic Model D", "Synthetic QA", "F1", "92.5"],
            ["Synthetic Model E", "Synthetic QA", "F1", "91.3"],
            ["Synthetic Model F", "Synthetic QA", "F1", "88.9"]]
    commands.append("0.7 w 54 510 m 558 510 l S")
    for i, row in enumerate(rows):
        for x, value in zip(columns, row):
            text(x, 490 - i * 27, value, 11, "F2" if i == 0 else "F1")
    commands += ["0.5 w 54 477 m 558 477 l S", "0.7 w 54 315 m 558 315 l S"]
    text(54, 280, "The largest score is 92.5 for Synthetic Model D on Synthetic QA.")
    text(54, 261, "Expected output: a readable table with a page number and numeric values.")
    text(54, 215, "3. Validation boundary", 14, "F2")
    text(54, 190, "This fixture checks software execution only. Gold dataset access is still required.")
    text(300, 35, "1", 10)
    stream = DecodedStreamObject()
    stream.set_data("\n".join(commands).encode("ascii"))
    page[NameObject("/Contents")] = writer._add_object(stream)
    path = OUT / "synthetic-diagnostic.pdf"
    writer.add_metadata({"/Title": "Synthetic SCILEAD environment diagnostic - NOT a SciLead paper"})
    writer.write(path)
    return path


PDF = OUT / "synthetic-diagnostic.pdf" if RETRIEVAL_ONLY else make_fixture()


def render_ocr():
    from pdf2image import pdfinfo_from_path, convert_from_path
    info = pdfinfo_from_path(str(PDF), poppler_path=str(POPPLER))
    assert info["Pages"] == 1
    images = convert_from_path(str(PDF), dpi=150, first_page=1, last_page=1, poppler_path=str(POPPLER))
    target = OUT / "synthetic-page-1.png"
    images[0].save(target)
    proc = subprocess.run([str(TESSERACT / "tesseract.exe"), str(target), "stdout", "--tessdata-dir", str(TESSERACT / "tessdata"), "-l", "eng"], capture_output=True, text=True, check=True)
    (OUT / "ocr.txt").write_text(proc.stdout, encoding="utf-8")
    assert "92.5" in proc.stdout and "Synthetic" in proc.stdout
    return {"pages": 1, "image_size": images[0].size, "ocr_contains_expected_score": True}


if not RETRIEVAL_ONLY:
    check("Poppler PDF rendering and English OCR", render_ocr)


def high_resolution():
    import torch
    torch.set_num_threads(4)
    from unstructured.partition.pdf import partition_pdf, default_hi_res_model
    assert default_hi_res_model() == "yolox"
    elements = partition_pdf(filename=str(PDF), strategy="hi_res", infer_table_structure=True)
    (OUT / "partition-elements.json").write_text(json.dumps([e.to_dict() for e in elements], indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    tables = [e.to_dict() for e in elements if e.category == "Table"]
    assert tables, "No table recognized; stop rather than changing strategy"
    assert any("92.5" in str(e["text"]) for e in tables), "Expected table score missing"
    assert any(e["metadata"].get("text_as_html") for e in tables), "Table structure HTML is missing"
    (OUT / "tables.json").write_text(json.dumps(tables, indent=2, ensure_ascii=False), encoding="utf-8")
    return {"strategy": "hi_res", "layout_model": "yolox", "table_structure": True, "elements": len(elements), "tables": len(tables), "table_pages": [e["metadata"].get("page_number") for e in tables]}


if not RETRIEVAL_ONLY and results["checks"]["Poppler PDF rendering and English OCR"]["status"] == "PASS":
    check("High resolution layout and table inference", high_resolution)


def retrieval():
    import torch
    torch.set_num_threads(4)
    from langchain_community.vectorstores import Chroma
    from langchain_community.embeddings import HuggingFaceEmbeddings
    from langchain_core.documents import Document
    from chromadb.config import Settings
    embeddings = HuggingFaceEmbeddings(model_name="multi-qa-mpnet-base-dot-v1")
    documents = [
        Document(page_content="Synthetic Model D achieved 92.5 F1 on the Synthetic QA dataset.", metadata={"source": "synthetic diagnostic", "page_number": 1}),
        Document(page_content="The orchard grows apples and pears during the summer.", metadata={"source": "synthetic distractor"}),
        Document(page_content="Synthetic Baseline A achieved 84.2 F1 on the Synthetic QA dataset.", metadata={"source": "synthetic diagnostic", "page_number": 1}),
        Document(page_content="Ocean tides change the water level along the coastline.", metadata={"source": "synthetic distractor"}),
        Document(page_content="The experiment compares synthetic question answering models using F1 scores.", metadata={"source": "synthetic diagnostic", "page_number": 1}),
    ]
    db = Chroma.from_documents(documents, embeddings, collection_name="scilead_diagnostic", client_settings=Settings(_env_file=None, anonymized_telemetry=False))
    question = "Which model achieves 92.5 F1 on Synthetic QA?"
    found = db.as_retriever(search_type="similarity").invoke(question)
    assert len(found) == 4
    assert "92.5" in found[0].page_content
    data = {"model": "multi-qa-mpnet-base-dot-v1", "device": str(embeddings.client.device), "documents_indexed": len(documents), "evidence_count": len(found), "query": question, "evidence": [{"text": d.page_content, "metadata": d.metadata} for d in found]}
    (OUT / "retrieval-evidence.json").write_text(json.dumps(data, indent=2), encoding="utf-8")
    db.delete_collection()
    return data


check("Original MPNet model and Chroma retrieval", retrieval)
save()
sys.exit(0 if all(v["status"] == "PASS" for v in results["checks"].values()) else 1)
