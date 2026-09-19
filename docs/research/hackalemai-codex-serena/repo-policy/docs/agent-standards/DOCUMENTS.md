# Documents, media and data artifacts

## Coverage boundary

PDF, DOCX, PPTX, XLSX, images, audio and video do not become semantically editable through a code LSP. Use the appropriate document/media API and inspect the rendered result. Notebook JSON requires notebook-aware cell handling. Text extraction and visual correctness are separate checks.

## Input ingestion

Preserve the original file and provenance. Detect actual format/type, enforce explicit limits and treat filenames/metadata as untrusted. Handle archives, oversized images, malformed files and remote URLs deliberately. Do not let document imports read arbitrary local paths or internal network endpoints.

Use Docling or a targeted parser according to structure requirements. Extract existing PDF text first when usable; OCR is a fallback for image content or inadequate extraction. For RU/KK/EN OCR, verify actual installed language models and quality. Do not treat a table, reading order, formula or handwritten answer as correctly extracted merely because a parser returned text.

Preserve source page/slide/sheet/cell or time offsets used in citations. Record uncertainty or extraction failures. Do not fill missing content from model imagination. An OCR/vision normalization step must not silently change the author's values or formula.

## Generated documents

For PDF/slides, use a reproducible source layout, supported fonts and deliberate page/slide dimensions. Render every changed page or slide and check overflow, clipped text, overlapping elements, missing assets, legibility and consistent alignment. Extracted text alone cannot establish visual quality.

For DOCX, preserve document structure, heading hierarchy, tables, lists, hyperlinks and page behavior. For PPTX, preserve actual slide objects rather than a single flattened image unless that is explicitly intended. Do not include internal developer notes, unresolved placeholders or unsupported success claims in the judged presentation.

For XLSX, preserve formulas, types, formats and references. Distinguish text beginning with `=` from an intended formula; prevent imported untrusted strings from being interpreted as executable spreadsheet formulas. Recalculate/verify important totals through a suitable engine or explicit independent computation and state cached-result limitations.

## Structured data and notebooks

For CSV/TSV, explicitly handle delimiter, quoting, encoding, newline, decimal conventions and missing values. Preserve large identifiers as strings where needed. For Parquet/Arrow, check schema/nullability and round-trip representative data.

Validate notebooks with nbformat-aware tools. Lint/typecheck appropriate Python cells or extracted modules without treating magic commands as ordinary Python. Do not rewrite the entire notebook container for a small cell change. Remove sensitive or irrelevant outputs from committed notebooks.

## Images and media

Check image dimensions, orientation, color/alpha behavior and readability. For audio/video, inspect streams with ffprobe and verify output playback, timestamps and subtitle synchronization. Transcription requires a language/quality check, especially for names, formulas and mixed-language speech.

Keep heavy OCR/vision/FFmpeg/transcription off the API event loop. Use bounded jobs and retain processing status and source identity. Clean up only known temporary files. Never delete original user data as a side effect of a formatter or preview process.
