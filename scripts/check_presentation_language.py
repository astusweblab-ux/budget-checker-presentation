"""Fail investor presentation checks when technical jargon leaks into copy."""

from __future__ import annotations

import argparse
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path


BANNED_TERMS: tuple[tuple[str, str], ...] = (
    (r"\bcheckout\b", "write about choosing and paying for a plan"),
    (r"\bwebhook\b", "write about automatic payment confirmation"),
    (r"\bsandbox\b", "write about test payments"),
    (r"\bproduction\b", "write about real launch, real payments or live operation"),
    (r"production[- ]?ключ", "write about real payment details or real access"),
    (r"\bseo\b", "write about being easier to find in search"),
    (r"\bmetadata\b", "write about better presentation in search and social sharing"),
    (r"\bhreflang\b", "write about correct language pages"),
    (r"\bsitemap\b", "write about search engines seeing the pages correctly"),
    (r"\bbackend\b", "write about the service or platform"),
    (r"\bfrontend\b", "write about the website or user-facing part"),
    (r"\bapi\b", "write about data exchange or service connection"),
    (r"\bi18n\b", "write about language support"),
    (r"\bsmoke\b", "write about final check before launch"),
    (r"\bdeploy\b", "write about launch or publication"),
    (r"\bliqpay\b", "write about payment acceptance"),
    (r"\bturnstile\b", "write about anti-bot protection"),
    (r"\bpostgres(?:ql)?\b", "write about the database only in technical docs"),
    (r"\bredis\b", "write about background processing only in technical docs"),
    (r"\bcelery\b", "write about background processing only in technical docs"),
    (r"\bsmtp\b", "write about email sending"),
    (r"\brunbook\b", "write about instructions or regular checks"),
    (r"task scheduler", "write about automatic regular checks"),
    (r"\blocalhost\b", "do not show local developer addresses in the investor page"),
    (r"\.env\b", "do not mention secret files in the investor page"),
    (r"\.git\b", "do not mention repository internals in the investor page"),
    (r"фід(?:и|ів|ам|ами)?", "write about real prices or partner data"),
    (r"фид(?:ы|ов|ам|ами)?", "write about real prices or partner data"),
    (r"production[- ]?keys?", "write about real payment details or real access"),
)


class PresentationTextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._ignored_tags: list[str] = []
        self.visible_parts: list[str] = []
        self.script_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() in {"style"}:
            self._ignored_tags.append(tag.lower())
        elif tag.lower() == "script":
            self._ignored_tags.append("script")

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if self._ignored_tags and self._ignored_tags[-1] == tag:
            self._ignored_tags.pop()

    def handle_data(self, data: str) -> None:
        if self._ignored_tags:
            if self._ignored_tags[-1] == "script":
                self.script_parts.append(data)
            return
        if data.strip():
            self.visible_parts.append(data)


def _read_copy(path: Path) -> list[tuple[str, str]]:
    parser = PresentationTextParser()
    content = path.read_text(encoding="utf-8")
    parser.feed(content)

    chunks: list[tuple[str, str]] = []
    chunks.extend(("visible text", part) for part in parser.visible_parts)

    script_text = "\n".join(parser.script_parts)
    for match in re.finditer(r":\s*(\"(?:\\.|[^\"\\])*\")", script_text):
        try:
            value = json.loads(match.group(1))
        except json.JSONDecodeError:
            continue
        if isinstance(value, str) and value.strip():
            chunks.append(("translation text", value))

    return chunks


def check_file(path: Path) -> list[str]:
    findings: list[str] = []
    for source, text in _read_copy(path):
        normalized = " ".join(text.split())
        if not normalized:
            continue
        for pattern, suggestion in BANNED_TERMS:
            if re.search(pattern, normalized, flags=re.IGNORECASE):
                findings.append(
                    f"{path}: investor presentation copy contains technical term "
                    f"{pattern!r} in {source}: {normalized!r}. "
                    f"Rewrite it in plain investor language: {suggestion}."
                )
    return findings


def default_paths(repo_root: Path) -> list[Path]:
    source_presentation = repo_root / "docs" / "PROJECT_PRESENTATION.html"
    public_index = repo_root / "index.html"
    if source_presentation.exists():
        paths = [source_presentation]
    elif public_index.exists():
        paths = [public_index]
    else:
        paths = [source_presentation]

    sibling_public_index = repo_root.parent / "budget-checker-presentation" / "index.html"
    if sibling_public_index.exists():
        paths.append(sibling_public_index)
    return paths


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check investor presentation HTML for technical jargon."
    )
    parser.add_argument(
        "paths",
        nargs="*",
        type=Path,
        help="Presentation HTML files to check. Defaults to source and sibling public index.",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    paths = args.paths or default_paths(repo_root)

    missing = [path for path in paths if not path.exists()]
    if missing:
        for path in missing:
            print(f"Missing presentation file: {path}", file=sys.stderr)
        return 2

    findings: list[str] = []
    for path in paths:
        findings.extend(check_file(path))

    if findings:
        print("Investor presentation language check failed.", file=sys.stderr)
        print(
            "This page is for investors. Replace technical terms with clear business language.",
            file=sys.stderr,
        )
        for finding in findings:
            print(f"- {finding}", file=sys.stderr)
        return 1

    checked = ", ".join(str(path) for path in paths)
    print(f"Investor presentation language check passed: {checked}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
