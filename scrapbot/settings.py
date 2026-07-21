BOT_NAME = "scrapbot"

SPIDER_MODULES = ["scrapbot.spiders"]
NEWSPIDER_MODULE = "scrapbot.spiders"

# Hedef sitenin robots.txt kurallarına uy.
ROBOTSTXT_OBEY = True

# Kitap sitesine gereksiz yük bindirmemek için temkinli varsayılanlar.
CONCURRENT_REQUESTS_PER_DOMAIN = 2
DOWNLOAD_DELAY = 0.75
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 0.75
AUTOTHROTTLE_MAX_DELAY = 10.0
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0

COOKIES_ENABLED = False
TELNETCONSOLE_ENABLED = False
FEED_EXPORT_ENCODING = "utf-8"
LOG_LEVEL = "INFO"

USER_AGENT = (
    "scrapbot/0.1 "
    "(+https://github.com/aricansoft2022/scrapbot; respectful educational scraper)"
)

