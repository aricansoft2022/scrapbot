from __future__ import annotations

import re
from collections.abc import Iterable
from urllib.parse import urlsplit, urlunsplit

import scrapy
from scrapy.http import Response
from scrapy.linkextractors import LinkExtractor


DETAILS_RE = re.compile(r"^/details/books/(?P<slug>[a-z0-9][a-z0-9-]*)/?$")
PAGE_RE = re.compile(
    r"^/books/(?P<slug>[a-z0-9][a-z0-9-]*)/pages/(?P<page>[a-z0-9][a-z0-9-]*)/?$"
)


class OpenStaxBookSpider(scrapy.Spider):
    """Yalnızca seçilen OpenStax kitabının sayfalarını takip eder."""

    name = "openstax_book"
    allowed_domains = ["openstax.org"]

    def __init__(self, url: str, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.input_url = self._normalize_input_url(url)
        self.book_slug, page_slug = self._parse_input_url(self.input_url)
        self.page_root = f"https://openstax.org/books/{self.book_slug}/pages/"
        self.initial_page_url = (
            self.input_url if page_slug else f"{self.page_root}preface"
        )
        self.link_extractor = LinkExtractor(
            allow=(rf"^https://openstax\.org/books/{re.escape(self.book_slug)}/pages/",),
            allow_domains=("openstax.org",),
            unique=True,
        )

    async def start(self):
        yield scrapy.Request(
            self.initial_page_url,
            callback=self.parse_page,
            errback=self._fallback_from_preface,
        )

    def _fallback_from_preface(self, failure):
        """Preface bulunmayan kitaplarda yaygın başlangıç sayfasını dene."""
        fallback_url = f"{self.page_root}1-introduction"
        if self.initial_page_url != fallback_url:
            self.logger.warning(
                "İlk sayfa alınamadı (%s); %s deneniyor",
                failure.value,
                fallback_url,
            )
            yield scrapy.Request(fallback_url, callback=self.parse_page)

    def parse_page(self, response: Response) -> Iterable[dict | scrapy.Request]:
        if not self._is_in_book_scope(response.url):
            self.logger.warning("Kapsam dışı yanıt atlandı: %s", response.url)
            return

        content = response.css("main.page-content")
        if not content:
            self.logger.warning("Kitap içeriği bulunamadı: %s", response.url)
        else:
            text_parts = content.xpath(".//text()[normalize-space()]").getall()
            heading_parts = response.xpath(
                "(//h1)[1]//text()[normalize-space()]"
            ).getall()
            content_heading_parts = content.xpath(
                "(.//h1 | .//h2)[1]//text()[normalize-space()]"
            ).getall()
            title = (
                self._clean_text(" ".join(heading_parts))
                or self._clean_text(" ".join(content_heading_parts))
                or response.url.rsplit("/", 1)[-1]
            )
            source_url = self._canonical_page_url(response.url)
            yield {
                "book_slug": self.book_slug,
                "page_slug": urlsplit(source_url).path.rstrip("/").rsplit("/", 1)[-1],
                "title": title,
                "language": response.css("html::attr(lang)").get() or "en",
                "source_url": source_url,
                "content_text": self._clean_text(" ".join(text_parts)),
                "content_html": content.get(),
                "license": "CC BY-NC-SA 4.0",
                "license_url": "https://creativecommons.org/licenses/by-nc-sa/4.0/",
                "attribution": f"Access for free at {source_url}",
                "usage_notice": (
                    "OpenStax states that this book may not be ingested into "
                    "large language models or generative AI offerings without permission."
                ),
            }

        for link in self.link_extractor.extract_links(response):
            next_url = self._canonical_page_url(link.url)
            if self._is_in_book_scope(next_url):
                yield response.follow(next_url, callback=self.parse_page)

    @staticmethod
    def _normalize_input_url(url: str) -> str:
        value = (url or "").strip()
        if not value:
            raise ValueError("Bir OpenStax kitap URL'si vermelisin.")
        parts = urlsplit(value)
        if parts.scheme not in {"http", "https"} or parts.hostname != "openstax.org":
            raise ValueError("Yalnızca https://openstax.org kitap URL'leri destekleniyor.")
        return urlunsplit(("https", "openstax.org", parts.path, "", ""))

    @staticmethod
    def _parse_input_url(url: str) -> tuple[str, str | None]:
        path = urlsplit(url).path
        if match := DETAILS_RE.fullmatch(path):
            return match.group("slug"), None
        if match := PAGE_RE.fullmatch(path):
            return match.group("slug"), match.group("page")
        raise ValueError(
            "URL /details/books/<kitap> veya /books/<kitap>/pages/<sayfa> "
            "biçiminde olmalı."
        )

    def _is_in_book_scope(self, url: str) -> bool:
        parts = urlsplit(url)
        match = PAGE_RE.fullmatch(parts.path)
        return (
            parts.scheme in {"http", "https"}
            and parts.hostname == "openstax.org"
            and match is not None
            and match.group("slug") == self.book_slug
        )

    @staticmethod
    def _canonical_page_url(url: str) -> str:
        parts = urlsplit(url)
        return urlunsplit(("https", "openstax.org", parts.path.rstrip("/"), "", ""))

    @staticmethod
    def _clean_text(value: str | None) -> str:
        return re.sub(r"\s+", " ", value or "").strip()
