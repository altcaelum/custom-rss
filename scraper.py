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
        els => els
        .map(e => ({
            title: e.innerText.trim(),
            href: e.href
        }))
        .filter(x =>
            x.title &&
            x.href &&
            x.title.length > 10 &&

            ![
                "tags",
                "blogs",
                "awards",
                "residents",
                "education",
                "competencies",
                "contact us",
                "marketplace",
                "dafes awards",
                "magistracy",
                "themes"
            ].includes(x.title.toLowerCase()) &&

            !x.href.includes("/tags") &&
            !x.href.includes("/residents") &&
            !x.href.includes("/awards") &&
            !x.href.includes("/education") &&
            !x.href.includes("/marketplace") &&
            !x.href.includes("/themes") &&
            !x.href.includes("/magistracy")
        )
        """)[:30]

        fg = FeedGenerator()
        fg.title(s["name"])
        fg.link(href=s["url"])
        fg.description(f"Generated feed for {s['name']}")

        seen = set()

        for item in links:
            if item["href"] in seen:
                continue

            seen.add(item["href"])

            entry = fg.add_entry()
            entry.title(item["title"])
            entry.link(href=item["href"])
            entry.guid(item["href"])
            entry.pubDate(datetime.now(UTC))

        fg.rss_file(s["feed"])

    browser.close()
