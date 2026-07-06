---
name: markitdown
description: "Convert documents, files, and web content to Markdown using Microsoft's MarkItDown — the native format for LLMs."
version: 1.0.0
author: Vilius Vystartas
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [document-conversion, markdown, pdf, ocr, transcription]
---

# MarkItDown

Converts files to Markdown for LLM consumption. Uses Microsoft's MarkItDown library.

## Supported input formats

- PDF
- PowerPoint (.pptx)
- Word (.docx)
- Excel (.xlsx, .xls)
- Images (.jpg, .png, etc.) — EXIF metadata + OCR
- Audio (.wav, .mp3) — EXIF metadata + speech transcription
- HTML
- Text-based formats (CSV → markdown tables, JSON, XML)
- ZIP files (iterates over contents)
- YouTube URLs (transcript)
- EPUB
- Outlook messages (.msg)

## Usage

### CLI (direct)
```bash
markitdown path/to/file.pdf
# or pipe
cat file.pdf | markitdown
# or save to file
markitdown file.pdf -o output.md
```

### Python API
```python
from markitdown import MarkItDown

md = MarkItDown()
result = md.convert("file.pdf")
print(result.text_content)
```

### Agent usage (in terminal)
```bash
markitdown <file>
```

## Installation

```bash
pip install markitdown
# Or with extras:
pip install "markitdown[pdf,docx,pptx,xlsx,audio-transcription]"
```

## Notes
- v0.1.5+ recommended
- Dependencies include: pdfminer, pytesseract (OCR), pydub (audio), python-pptx, python-docx, openpyxl
- Security: markitdown performs I/O with the same privileges as the current process. Sanitize untrusted inputs.
