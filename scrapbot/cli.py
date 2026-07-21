from __future__ import annotations

import argparse
from pathlib import Path

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from scrapbot.spiders.openstax_book import OpenStaxBookSpider


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="scrapbot",
        description="Tek bir OpenStax kitabını kapsam dışına çıkmadan kazır.",
    )
    parser.add_argument(
        "url",
        help=(
            "OpenStax kitap ayrıntı veya bölüm URL'si; örn. "
            "https://openstax.org/details/books/prealgebra-2e"
        ),
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("data/book.jsonl"),
        help="JSONL çıktı yolu (varsayılan: data/book.jsonl)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    args.output.parent.mkdir(parents=True, exist_ok=True)

    settings = get_project_settings()
    settings.set(
        "FEEDS",
        {
            str(args.output.resolve()): {
                "format": "jsonlines",
                "encoding": "utf-8",
                "overwrite": True,
            }
        },
        priority="cmdline",
    )

    process = CrawlerProcess(settings)
    process.crawl(OpenStaxBookSpider, url=args.url)
    process.start()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

