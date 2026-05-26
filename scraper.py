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

BLACKLIST = [
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

        items = page.locator("a").evaluate_all("""
        els => els.map(e => ({

            title: e.innerText.trim(),
            href: e.href,

            image:
                e.querySelector("img")?.src || "",

            description:
                e.parentElement?.innerText || ""

        }))
        """)

        filtered = []
        seen = set()

        for item in items:

            title = item["title"].strip().lower()
            href = item["href"]

            if not title:
                continue

            if len(title) < 10:
                continue

            if href in seen:
                continue

            if title in BLACKLIST:
                continue

            if any(x in href.lower() for x in [
                "/tags",
                "/awards",
                "/residents",
                "/education",
                "/themes",
                "/marketplace",
                "/magistracy"
            ]):
                continue

            seen.add(href)
            filtered.append(item)

        fg = FeedGenerator()

        fg.title(s["name"])
        fg.link(href=s["url"])
        fg.description(
            f"Custom RSS for {s['name']}"
        )

        for item in filtered[:25]:

            entry = fg.add_entry()

            entry.title(item["title"])

            entry.link(
                href=item["href"]
            )

            entry.guid(
                item["href"]
            )

            entry.description(
                item["description"][:500]
            )

            if item["image"]:
                entry.enclosure(
                    item["image"],
                    0,
                    "image/jpeg"
                )

            entry.pubDate(
                datetime.now(UTC)
            )

        fg.rss_file(
            s["feed"]
        )

    browser.close()
