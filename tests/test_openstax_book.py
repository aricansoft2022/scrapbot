from scrapy.http import HtmlResponse, Request

from scrapbot.spiders.openstax_book import OpenStaxBookSpider


def make_response(url: str, body: str) -> HtmlResponse:
    request = Request(url=url)
    return HtmlResponse(url=url, request=request, body=body, encoding="utf-8")


def test_details_url_starts_from_preface():
    spider = OpenStaxBookSpider(
        url="https://openstax.org/details/books/prealgebra-2e"
    )

    assert spider.book_slug == "prealgebra-2e"
    assert spider.initial_page_url == (
        "https://openstax.org/books/prealgebra-2e/pages/preface"
    )


def test_parse_extracts_content_and_follows_only_same_book():
    spider = OpenStaxBookSpider(
        url="https://openstax.org/details/books/prealgebra-2e"
    )
    response = make_response(
        "https://openstax.org/books/prealgebra-2e/pages/1-introduction",
        """
        <html lang="en"><body>
          <h1><span>Introduction</span></h1>
          <main class="page-content">
            <h2>Chapter Outline</h2><p>Hello,   world.</p>
            <a href="/books/prealgebra-2e/pages/1-1-whole-numbers">Next</a>
            <a href="/books/algebra-2e/pages/1-introduction">Other book</a>
            <a href="/details/books/prealgebra-2e">Details</a>
          </main>
        </body></html>
        """,
    )

    results = list(spider.parse_page(response))
    items = [result for result in results if isinstance(result, dict)]
    requests = [result for result in results if isinstance(result, Request)]

    assert len(items) == 1
    assert items[0]["title"] == "Introduction"
    assert "Hello, world." in items[0]["content_text"]
    assert items[0]["attribution"].endswith("/1-introduction")
    assert [request.url for request in requests] == [
        "https://openstax.org/books/prealgebra-2e/pages/1-1-whole-numbers"
    ]


def test_query_and_fragment_are_removed_from_page_input():
    spider = OpenStaxBookSpider(
        url=(
            "https://openstax.org/books/prealgebra-2e/pages/1-introduction"
            "?utm_source=test#main"
        )
    )

    assert spider.initial_page_url == (
        "https://openstax.org/books/prealgebra-2e/pages/1-introduction"
    )


def test_rejects_urls_outside_openstax():
    try:
        OpenStaxBookSpider(url="https://example.com/details/books/prealgebra-2e")
    except ValueError as error:
        assert "openstax.org" in str(error)
    else:
        raise AssertionError("Kapsam dışı URL reddedilmeliydi")
