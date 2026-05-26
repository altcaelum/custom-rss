from playwright.sync_api import sync_playwright
from feedgen.feed import FeedGenerator
from datetime import datetime, UTC

sites = [
    {
        "name": "deziiign",
        "url": "https://deziiign.com/",
        "feed": "deziiign.xml"
    },
    {
        "name": "mediiia",
        "url": "https://mediiia.com/",
        "feed": "mediiia.xml"
    }
]

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()

    for s in sites:
        page.goto(
            s["url"],
            wait_until="domcontentloaded",
            timeout=60000
        )

        page.wait_for_timeout(5000)

        links = page.locator("a").evaluate_all("""
            els => els.map(e => ({
                title: e.innerText,
                href: e.href
            })).filter(x => x.title && x.href)
        """)[:20]

        fg = FeedGenerator()
        fg.title(s["name"])
        fg.link(href=s["url"])
        fg.description(f"Generated feed for {s['name']}")

        for item in links:
            entry = fg.add_entry()
            entry.title(item["title"])
            entry.link(href=item["href"])
            entry.guid(item["href"])
            entry.pubDate(datetime.now(UTC))

        fg.rss_file(s["feed"])

    browser.close()
