# Documents

Universe: `build/stack-pin.json` `media.*` except
`media.livekit` (EDUCATION + INFRA `live`),
`environments.api_workers`, `environments.gpu_ml`,
`quality.playwright`, `data.*`. Conflict
`docling-opencv-cv2`. Reports: HTML/CSS + Playwright
Chromium in a worker — not this ingest path.

Unless the owner said otherwise this turn.

This file is how files become text + citations. DATA owns
bytes and keys. AI owns embeddings after extract. Do not
create workers only to hold this file.

## Default move

1. API authorizes, presigns PUT, writes Postgres metadata.
   `HeadObject` → `ready` → Taskiq. Bytes never enter a
   parser on the request path.
2. Taskiq on `api_workers` probes and parses light formats
   (pypdf, python-docx / pptx, openpyxl, trafilatura). It
   does not import Docling Standard, RapidOCR, tesseract,
   torch, or faster-whisper.
3. Structure, OCR, layout, tables, HybridChunker, and
   transcription enqueue to `gpu_ml`. Persist AI’s embedding
   identity string on the chunk row. Original stays.
   Derived objects under DATA’s `drv/` prefix.
4. Citations are stored with the extract. Unknown offsets
   stay unknown.

## Pattern

### Graphs

`api_workers` may share FastAPI + Taskiq — that is why
`docling[standard]` / RapidOCR / torch cannot be in that
lock. `gpu_ml` owns: `docling-slim` extras **without**
`standard` / `feat-ocr-rapidocr`, system Tesseract
`rus+kaz+eng`, opencv-python-headless only, faster-whisper.
One `cv2`. Do not `uv add docling` unconstrained.

### PDF

Probe every PDF in Taskiq with pypdf: encryption, text
length per page, image count.

| Probe | Extractor | Where | Citations |
| --- | --- | --- | --- |
| Usable text, no tables needed | pypdf `extract_text` + `visitor_text` (plain) | `api_workers` | page + excerpt + `xy` |
| Usable text + structure | Docling Standard, `do_ocr=False` | `gpu_ml` | `ProvenanceItem` bbox + `charspan` |
| Empty / scan / image | Standard + `TesseractCliOcrOptions` | `gpu_ml` | bbox + ocr meta |

Do not use pypdf `extraction_mode="layout"` for citations
(visitors dropped). Do not use `OcrAutoOptions` (picks
RapidOCR / `ch`). Always set `do_ocr` — Docling defaults
True. `layout` visitors: `x,y = pypdf.mult(tm, cm)[4:6]`.

Tesseract: `lang=["rus","kaz","eng"]`. Prove
`tesseract --list-langs` on the image. Missing tessdata is
FAILURE, not a silent `eng`. RapidOCR / EasyOCR / Nemotron
/ ocrmac / `docling[asr]` are out.

### Office / HTML / media

- DOCX / PPTX / XLSX: native libs in Taskiq. Cite para /
  slide+shape / sheet+A1. python-docx has **no page
  numbers**. XLSX: formulas and cached values are two
  reads (`data_only`).
- HTML ingest: trafilatura. Cite URL + node. Playwright
  HTML reporter is a QA artifact, not a source document.
- Audio/video: ffprobe in Taskiq (metadata), faster-whisper
  in `gpu_ml` with `word_timestamps`. Cite `[t0,t1]`.
- Images: Tesseract in `gpu_ml`. Pillow / headless OpenCV
  for decode. Not on the API event loop.

### Citations

Store: `source_id`, `kind`, page/slide/sheet/cell/para/
shape, `bbox`, `charspan` (intra-item), `xy`, `t0`/`t1`,
`excerpt`, `extractor`, `ocr` meta. Do not cite a page or
timestamp that was not extracted. HybridChunker must copy
`prov` onto chunks. Qdrant payload mirrors this; Postgres
is SoT.

### Reports

`media.reports`: render HTML/CSS in a Taskiq worker, print
via pin Playwright/Chromium, store the PDF under DATA
`drv/`. Not a request-path render. Not a source document
for ingest. LiveKit is not this file.

### Never in the API process

No `DocumentConverter`, no `WhisperModel`, no tesseract
subprocess, no RapidOCR, no torch, no OpenCV decode of
student bytes. `BackgroundTasks` is not a worker.

## Done

- Original in RustFS; Postgres has checksum, mime, owner,
  status, probe, chosen path.
- Offsets persisted. Failures are FAILURE, not empty
  SUCCESS.
- `api_workers` lock has no `docling[standard]`, RapidOCR,
  or torch. One `cv2` in `gpu_ml`. Tesseract langs proven.
- Playwright HTML report stayed a test artifact.

## Repair

- Torch / RapidOCR / `opencv-python` in `api_workers`:
  revert; keep constrained extras in `gpu_ml`.
- OCR on a digital text layer: `do_ocr=False`.
- Missing `kaz`/`rus` tessdata: fail the job.
- Citation without page/slide/cell/time: do not ship the
  answer.
