# app/rag.py
import glob
import json
import os
import pathlib

import chardet
import docx2txt
import numpy as np
import yaml
from fastembed import TextEmbedding
from markdown_it import MarkdownIt
from pypdf import PdfReader


def load_config():
    with open(
        os.path.join(pathlib.Path(__file__).resolve().parent, "config.yaml"),
        "r",
        encoding="utf-8",
    ) as f:
        return yaml.safe_load(f)


def read_text_file(path):
    with open(path, "rb") as f:
        raw = f.read()
    enc = chardet.detect(raw)["encoding"] or "utf-8"
    try:
        return raw.decode(enc, errors="ignore")
    except Exception:
        return raw.decode("utf-8", errors="ignore")


def extract_text(path):
    p = str(path).lower()
    if p.endswith(".pdf"):
        try:
            reader = PdfReader(path)
            return "\n\n".join(
                [page.extract_text() or "" for page in reader.pages]
            )
        except Exception:
            return ""
    if p.endswith(".docx"):
        try:
            return docx2txt.process(path) or ""
        except Exception:
            return ""
    if p.endswith(".md"):
        txt = read_text_file(path)
        # Keep raw markdown; it's usually fine. Optionally strip markup:
        md = MarkdownIt()
        return md.render(txt)
    if p.endswith(".txt"):
        return read_text_file(path)
    return ""


def chunk_text(text, chunk_chars=1200, overlap=200):
    chunks = []
    i = 0
    n = len(text)
    while i < n:
        j = min(i + chunk_chars, n)
        chunk = text[i:j]
        chunks.append(chunk.strip())
        i = j - overlap
        if i < 0:
            i = 0
        if i >= n:
            break
    return [c for c in chunks if c]


class RAG:
    def __init__(self, cfg):
        self.cfg = cfg
        self.kb_dir = cfg["index"]["kb_dir"]
        self.index_dir = cfg["index"]["dir"]
        os.makedirs(self.index_dir, exist_ok=True)
        self.chunk_chars = cfg["index"]["chunk_chars"]
        self.chunk_overlap = cfg["index"]["chunk_overlap"]
        self.embed = TextEmbedding(model_name=cfg["embedder"]["model"])
        self.dim = cfg["embedder"]["dim"]
        self.emb_path = os.path.join(self.index_dir, "embeddings.npy")
        self.meta_path = os.path.join(self.index_dir, "meta.jsonl")
        self._emb = None
        self._meta = None
        self._load_index_if_exists()

    def _load_index_if_exists(self):
        if os.path.exists(self.emb_path) and os.path.exists(self.meta_path):
            try:
                self._emb = np.load(self.emb_path)
                with open(self.meta_path, "r", encoding="utf-8") as f:
                    self._meta = [json.loads(line) for line in f]
                # normalize
                norms = (
                    np.linalg.norm(self._emb, axis=1, keepdims=True) + 1e-12
                )
                self._emb = self._emb / norms
            except Exception:
                self._emb = None
                self._meta = None

    def build_index(self):
        files = []
        for ext in ("*.pdf", "*.docx", "*.txt", "*.md"):
            files.extend(
                glob.glob(os.path.join(self.kb_dir, "**", ext), recursive=True)
            )

        meta = []
        chunks = []
        for fp in files:
            txt = extract_text(fp)
            if not txt:
                continue
            parts = chunk_text(txt, self.chunk_chars, self.chunk_overlap)
            for idx, ch in enumerate(parts):
                meta.append(
                    {
                        "path": os.path.relpath(fp, self.kb_dir),
                        "chunk_id": idx,
                        "chars": len(ch),
                    }
                )
                chunks.append(ch)

        if not chunks:
            # empty index
            self._emb = np.zeros((0, self.dim), dtype=np.float32)
            self._meta = []
            np.save(self.emb_path, self._emb)
            open(self.meta_path, "w", encoding="utf-8").close()
            return 0

        # embed in batches
        vecs = []
        for emb in self.embed.embed(chunks, batch_size=64):
            vecs.append(np.array(emb, dtype=np.float32))
        E = np.vstack(vecs)
        # L2 normalize for cosine
        norms = np.linalg.norm(E, axis=1, keepdims=True) + 1e-12
        E = E / norms

        # save
        np.save(self.emb_path, E)
        with open(self.meta_path, "w", encoding="utf-8") as f:
            for m in meta:
                f.write(json.dumps(m, ensure_ascii=False) + "\n")

        self._emb = E
        self._meta = meta
        return len(meta)

    def retrieve(self, query, k=5):
        if self._emb is None or self._meta is None or len(self._meta) == 0:
            return []
        qv = np.array(list(self.embed.embed([query]))[0], dtype=np.float32)
        qv = qv / (np.linalg.norm(qv) + 1e-12)
        sims = (self._emb @ qv).astype(np.float32)
        topk = int(max(1, min(k, len(sims))))
        idxs = np.argsort(-sims)[:topk].tolist()

        results = []
        # Load chunk texts by reading file and chunking
        for i in idxs:
            m = self._meta[i]
            fp = os.path.join(self.kb_dir, m["path"])
            txt = extract_text(fp)
            parts = chunk_text(txt, self.chunk_chars, self.chunk_overlap)
            chunk_text_str = (
                parts[m["chunk_id"]] if m["chunk_id"] < len(parts) else ""
            )
            results.append(
                {
                    "path": m["path"],
                    "chunk_id": m["chunk_id"],
                    "text": chunk_text_str,
                }
            )
        return results

    def build_prompt(self, query, contexts):
        header = (
            "Use ONLY the context below to answer. If the answer "
            "isn't present, say you don't have enough info.\n\n"
        )
        ctx = "\n\n---\n\n".join(
            [
                f"Source: {c['path']}#chunk{c['chunk_id']}\n{c['text']}"
                for c in contexts
            ]
        )
        return header + ctx + f"\n\nQuestion: {query}\nAnswer:"
