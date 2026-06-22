from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from zipfile import ZipFile
import xml.etree.ElementTree as ET


class DocumentParseError(RuntimeError):
    pass


@dataclass(frozen=True)
class ParsedDocument:
    filename: str
    content_type: str
    text: str
    word_count: int


class DocumentParser:
    def parse(self, *, filename: str, content: bytes, content_type: str | None = None) -> ParsedDocument:
        suffix = Path(filename).suffix.lower()
        if suffix in {".txt", ".md"}:
            text = self._decode_text(content)
        elif suffix == ".docx":
            text = self._parse_docx(content)
        elif suffix == ".pdf":
            text = self._parse_pdf(content)
        else:
            raise DocumentParseError(f"Unsupported document type: {suffix or 'unknown'}")

        normalized = self._normalize(text)
        if not normalized:
            raise DocumentParseError("Document contains no readable text")
        return ParsedDocument(
            filename=filename,
            content_type=content_type or "application/octet-stream",
            text=normalized,
            word_count=len(normalized.split()),
        )

    def _decode_text(self, content: bytes) -> str:
        for encoding in ("utf-8", "utf-8-sig", "gb18030"):
            try:
                return content.decode(encoding)
            except UnicodeDecodeError:
                continue
        raise DocumentParseError("Unable to decode text document")

    def _parse_docx(self, content: bytes) -> str:
        try:
            with ZipFile(self._bytes_path(content)) as archive:
                xml = archive.read("word/document.xml")
        except Exception as exc:
            raise DocumentParseError("Unable to parse docx document") from exc

        namespace = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
        root = ET.fromstring(xml)
        paragraphs: list[str] = []
        for paragraph in root.findall(".//w:p", namespace):
            parts = [node.text or "" for node in paragraph.findall(".//w:t", namespace)]
            if parts:
                paragraphs.append("".join(parts))
        return "\n".join(paragraphs)

    def _parse_pdf(self, content: bytes) -> str:
        try:
            from pypdf import PdfReader
        except ImportError as exc:
            raise DocumentParseError("PDF parsing requires pypdf to be installed") from exc

        try:
            import io

            reader = PdfReader(io.BytesIO(content))
            return "\n".join(page.extract_text() or "" for page in reader.pages)
        except Exception as exc:
            raise DocumentParseError("Unable to parse pdf document") from exc

    def _normalize(self, text: str) -> str:
        lines = [" ".join(line.split()) for line in text.splitlines()]
        return "\n".join(line for line in lines if line).strip()

    def _bytes_path(self, content: bytes):
        import io

        return io.BytesIO(content)
