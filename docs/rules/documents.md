# Documents and media

| Tool | Pin | Role |
| --- | --- | --- |
| Docling | `2.129.0` | Ingest. Default extra `standard` is not API-safe |
| pypdf | `6.19.0` | Non-Docling PDF path |
| Tesseract | langs `rus`, `kaz`, `eng` | OCR |
| Pillow | `12.3.0` | Images |
| opencv-python-headless | `5.0.0.93` | Only `cv2`. Constrain `opencv-python` |
| python-docx | `1.2.0` | Word |
| python-pptx | `1.0.2` | Slides |
| openpyxl | `3.1.5` | Excel |
| trafilatura | `2.2.0` | HTML extract |
| faster-whisper | `1.2.1` in `gpu_ml` | Speech |
| FFmpeg + ffprobe | host tools | Media |
| sympy | `1.14.0` | Compute (also education) |

Do not `uv add docling` unconstrained. Extra `standard` pulls RapidOCR
(`opencv-python`) and torch. Constrain `opencv-python`. Keep that graph
in `gpu_ml` or a dedicated ingest env. Docling rasterizes via pypdfium2;
do not treat `pypdf` as Docling’s renderer.

Binaries live in RustFS, not git. Reports are HTML/CSS rendered with
Playwright/Chromium.

Notebooks, CSV-as-SoT, and “Context7 MCP required” are not pinned.
LiveKit is optional realtime, not a document pipeline.
