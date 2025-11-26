import hashlib
from pathlib import Path
from pypdf import PdfReader

def text_hash(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()

def load_pdf(path: Path) -> str:
    reader = PdfReader(str(path))
    text = ""
    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted + "\n"
    return text

def load_text_from_file(path: str) -> str:
    path = Path(path)
    ext = path.suffix.lower()

    print(f"[loader] Loading: {path} ({ext})")

    if ext in [".txt", ".md"]:
        return path.read_text(encoding="utf-8", errors="ignore")

    if ext == ".pdf":
        return load_pdf(path)

    return ""  # unsupported formats

def load_documents(folder: Path):
    docs = []
    folder = Path(folder)

    print(f"[loader] Scanning folder: {folder.resolve()}")

    for file in folder.iterdir():
        if file.suffix.lower() not in [".pdf", ".txt", ".md"]:
            print(f"[loader] Skipped: {file.name}")
            continue

        text = load_text_from_file(file)
        if len(text.strip()) == 0:
            print(f"[loader] WARNING: No text extracted from {file.name}")

        docs.append({
            "filename": file.name,
            "text": text
        })

    print(f"[loader] Loaded documents: {len(docs)}")
    return docs
