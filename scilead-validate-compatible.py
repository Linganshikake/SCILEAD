"""Offline dependency/API smoke checks; does not run SCILEAD or parse PDFs."""
import ast
import hashlib
import importlib
import importlib.metadata as metadata
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
REPO = ROOT / "emnlp2024-leaderboard-generation"
GIT = ["git", "-c", "safe.directory=" + REPO.as_posix()]
assert Path(sys.executable) == Path(r"D:\miniconda3\envs\scilead\python.exe")
os.environ["HF_HOME"] = str(ROOT / ".scilead-validation-cache")
(ROOT / ".scilead-validation-cache" / "hub").mkdir(parents=True, exist_ok=True)
for name in ("HF_HUB_OFFLINE", "TRANSFORMERS_OFFLINE", "HF_HUB_DISABLE_TELEMETRY"):
    os.environ[name] = "1"
for name in ("LANGCHAIN_TRACING", "LANGCHAIN_TRACING_V2", "LANGSMITH_TRACING"):
    os.environ[name] = "false"
os.environ["DO_NOT_TRACK"] = "1"


def guard(event, args):
    if event in ("socket.connect", "socket.getaddrinfo"):
        raise RuntimeError("Network blocked by offline validation")
    if event == "open" and isinstance(args[0], (str, bytes)):
        path = os.fsdecode(args[0]).replace("\\", "/").lower()
        if Path(path).name.startswith(".env") or "/.codex/" in path or "/.aws/" in path:
            raise RuntimeError("Sensitive configuration access blocked")


sys.addaudithook(guard)
results = {"python": sys.version, "executable": sys.executable, "checks": {}, "optional": {}}


def check(name, fn, optional=False):
    target = results["optional" if optional else "checks"]
    try:
        detail = fn()
        target[name] = {"status": "PASS", "detail": detail}
    except Exception as exc:
        target[name] = {"status": "UNAVAILABLE" if optional else "FAIL", "detail": f"{type(exc).__name__}: {exc}"}
    print(name + ": " + json.dumps(target[name]), flush=True)


PACKAGES = {
    "numpy": "numpy", "torch": "torch", "pandas": "pandas",
    "langchain": "langchain", "langchain-community": "langchain_community",
    "langchain-core": "langchain_core", "langchain-openai": "langchain_openai",
    "transformers": "transformers", "sentence-transformers": "sentence_transformers",
    "unstructured": "unstructured", "python-dotenv": "dotenv",
    "ml-collections": "ml_collections", "rbo": "rbo", "requests": "requests", "tqdm": "tqdm",
}
for dist, module in PACKAGES.items():
    def import_package(dist=dist, module=module):
        importlib.import_module(module)
        return metadata.version(dist)
    check("import " + dist, import_package)


def foundation():
    import numpy as np
    import torch
    assert np.__version__ == "1.26.4"
    assert torch.__version__ == "2.2.0+cpu"
    assert torch.version.cuda is None and not torch.cuda.is_available()
    array = np.array([1., 2., 3.], dtype=np.float32)
    tensor = torch.from_numpy(array)
    tensor[0] = 7
    assert array[0] == 7
    np.testing.assert_array_equal((tensor * 2).numpy(), [14., 4., 6.])
    x = torch.tensor([2., 3.], requires_grad=True)
    x.square().sum().backward()
    np.testing.assert_array_equal(x.grad.numpy(), [4., 6.])
    return {"torch": torch.__version__, "numpy": np.__version__, "cuda": False, "autograd": "PASS"}


check("CPU Torch and NumPy interop", foundation)


def pinned_requirements():
    from packaging.requirements import Requirement
    count = 0
    for filename in ("requirements-scilead-win-cpu-compatible.txt", "constraints-scilead-win-cpu.txt"):
        for line in (ROOT / filename).read_text(encoding="utf-8").splitlines():
            if not line.strip() or line.startswith("#"):
                continue
            req = Requirement(line)
            assert metadata.version(req.name) in req.specifier, line
            count += 1
    import requests
    requests.check_compatibility(metadata.version("urllib3"), metadata.version("chardet"), metadata.version("charset-normalizer"))
    return {"pins_checked": count, "requests_runtime_dependency_check": "PASS"}


check("All pinned requirements and Requests compatibility", pinned_requirements)


def legacy_api():
    from langchain.chains import RetrievalQA
    from langchain.callbacks import get_openai_callback
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain.prompts.prompt import PromptTemplate
    from langchain_openai import ChatOpenAI, AzureChatOpenAI
    from langchain_community.vectorstores import Chroma
    from langchain_community.embeddings import HuggingFaceEmbeddings
    from langchain_core.vectorstores import VectorStoreRetriever
    from langchain_core.retrievers import BaseRetriever
    from langchain_core.callbacks import CallbackManagerForRetrieverRun
    from langchain_core.documents import Document
    from langchain_core.prompts.chat import ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate
    assert callable(RetrievalQA.from_chain_type)
    assert callable(Chroma.from_documents)
    assert callable(HuggingFaceEmbeddings.embed_documents)
    assert callable(ChatOpenAI.invoke) and callable(AzureChatOpenAI.invoke)
    splitter = RecursiveCharacterTextSplitter(chunk_size=24, chunk_overlap=3)
    chunks = splitter.split_documents([Document(page_content="Local scientific leaderboard dependency check. " * 3)])
    assert len(chunks) > 1
    assert PromptTemplate.from_template("Hello {name}").format(name="SCILEAD") == "Hello SCILEAD"
    return "All requested symbols and SCILEAD legacy import paths available; splitter/prompt executed locally."


check("LangChain legacy APIs", legacy_api)


def retrieval_qa():
    from langchain.chains import RetrievalQA
    from langchain_community.llms.fake import FakeListLLM
    from langchain_core.retrievers import BaseRetriever
    from langchain_core.documents import Document
    class LocalRetriever(BaseRetriever):
        def _get_relevant_documents(self, query, *, run_manager):
            return [Document(page_content="The offline test result is 42.")]
    qa = RetrievalQA.from_chain_type(llm=FakeListLLM(responses=["42"]), retriever=LocalRetriever(), return_source_documents=True)
    output = qa.invoke({"query": "What is the test result?"})
    assert output["result"] == "42" and len(output["source_documents"]) == 1
    return "PASS: fake local LLM + in-memory retriever, result=42; no provider client/model."


check("RetrievalQA local invocation", retrieval_qa)


def embeddings_math():
    import torch
    from transformers import BertConfig, AutoTokenizer, AutoModelForCausalLM
    from sentence_transformers import SentenceTransformer, util
    config = BertConfig(hidden_size=16, num_attention_heads=2, num_hidden_layers=1)
    assert config.hidden_size == 16
    scores = util.cos_sim(torch.tensor([[1., 0.]]), torch.tensor([[1., 0.], [0., 1.]]))
    assert torch.allclose(scores, torch.tensor([[1., 0.]]))
    return "Transformers config and Sentence Transformers cosine similarity PASS; no from_pretrained/encode/model loading."


check("Transformers and Sentence Transformers", embeddings_math)


def unstructured_elements():
    from unstructured.documents.elements import Text, Table
    assert str(Text("local text")) == "local text"
    assert Table("local table").category == "Table"
    return "Text/Table objects available; no document parsing."


check("Unstructured basic elements", unstructured_elements)
check("Chroma backend", lambda: metadata.version("chromadb"), optional=True)
check("Unstructured PDF import only", lambda: str(importlib.import_module("unstructured.partition.pdf").partition_pdf.__name__), optional=True)


def nltk_resources():
    import nltk
    found = {}
    for resource in ("tokenizers/punkt", "taggers/averaged_perceptron_tagger", "tokenizers/punkt_tab/english", "taggers/averaged_perceptron_tagger_eng"):
        try:
            nltk.data.find(resource)
            found[resource] = "present"
        except LookupError:
            found[resource] = "missing"
    return found


check("NLTK resources (no download)", nltk_resources, optional=True)
results["system_tools_on_path"] = {name: shutil.which(name) for name in ("pdftoppm", "pdfinfo", "tesseract")}
results["pdf_optional_distributions"] = {}
for dist in ("pdfminer.six", "pillow-heif", "unstructured-inference", "unstructured.pytesseract", "pdf2image", "onnxruntime", "chromadb"):
    try:
        results["pdf_optional_distributions"][dist] = metadata.version(dist)
    except metadata.PackageNotFoundError:
        results["pdf_optional_distributions"][dist] = "not installed"


def integrity():
    raw = (REPO / "requirements.txt").read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    assert digest == "9a074c4962e8dd756bf46ee5bf87d54b75f09542a9de0e16da3962b037e4adf1"
    files = subprocess.check_output(GIT + ["ls-files", "--", "*.py"], cwd=REPO, text=True).splitlines()
    for name in files:
        ast.parse((REPO / name).read_text(encoding="utf-8-sig"), filename=name)
    subprocess.run(GIT + ["diff", "--quiet", "HEAD", "--", "requirements.txt", "*.py"], cwd=REPO, check=True)
    return {"official_requirements_sha256": digest, "syntax_files": len(files), "source_unchanged": True}


check("Repository integrity and syntax", integrity)
results["git_commit"] = subprocess.check_output(GIT + ["rev-parse", "HEAD"], cwd=REPO, text=True).strip()
pip_result = subprocess.run([sys.executable, "-m", "pip", "--isolated", "--disable-pip-version-check", "check"], capture_output=True, text=True)
results["checks"]["pip check"] = {"status": "PASS" if pip_result.returncode == 0 else "FAIL", "exit_code": pip_result.returncode, "detail": (pip_result.stdout + pip_result.stderr).strip()}
results["installed_versions"] = {dist.metadata["Name"]: dist.version for dist in metadata.distributions()}
# Standard pip freeze excludes Conda's pip bootstrap file URL on Python 3.11.
# All installed distributions, including bootstrap tools, are recorded above.
freeze = subprocess.check_output([sys.executable, "-m", "pip", "--isolated", "--disable-pip-version-check", "freeze"], text=True)
assert " @ " not in freeze, "Review URL requirements before recording"
(ROOT / "scilead-win-cpu-freeze.txt").write_text(freeze, encoding="utf-8")
(ROOT / "scilead-compatible-validation.json").write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
print(json.dumps(results, indent=2), flush=True)
sys.exit(0 if all(item["status"] == "PASS" for item in results["checks"].values()) else 1)
