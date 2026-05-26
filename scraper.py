from playwright.sync_api import sync_playwright
from feedgen.feed import FeedGenerator
from datetime import datetime, UTC

sites = [
    {
        "name":"deziiign",
        "url":"https://deziiign.com/",
        "feed":"deziiign.xml"
    },
    {
        "name":"mediiia",
        "url":"https://mediiia.com/",
        "feed":"mediiia.xml"
    },
    {
        "name":"mediiia-books",
        "url":"https://mediiia.com/books",
        "feed":"mediiia-books.xml"
    }
]

BLACKLIST=[
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

    browser=p.chromium.launch()

    page=browser.new_page()

    for s in sites:

        page.goto(
            s["url"],
            wait_until="domcontentloaded",
            timeout=60000
        )

        page.wait_for_timeout(1500)

        links=page.locator("a").evaluate_all("""
        els => els.map(e=>({
            title:e.innerText.trim(),
            href:e.href
        }))
        """)

        unique=[]
        seen=set()

        for item in links:

            title=item["title"].lower()

            if len(title)<10:
                continue

            if item["href"] in seen:
                continue

            if title in BLACKLIST:
                continue

            seen.add(item["href"])
            unique.append(item)

        fg=FeedGenerator()

        fg.title(s["name"])
        fg.link(href=s["url"])
        fg.description(s["name"])

        for item in unique[:8]:

            try:

                article=browser.new_page()

                article.goto(
                    item["href"],
                    wait_until="domcontentloaded",
                    timeout=30000
                )

                article.wait_for_timeout(1000)

                text=article.locator("body").inner_text()

                image=""

                imgs=article.locator("img")

                if imgs.count()>0:
                    image=imgs.nth(0).get_attribute("src") or ""

                html=""

                if image:
                    html += f'<img src="{image}"><br><br>'

                html += f"<p>{text[:3000]}</p>"

                entry=fg.add_entry()

                entry.title(item["title"])
                entry.guid(item["href"])
                entry.link(href=item["href"])

                entry.description(
                    text[:500]
                )

                entry.content(
                    html
                )

                entry.pubDate(
                    datetime.now(UTC)
                )

                article.close()

            except:
                pass

        fg.rss_file(
            s["feed"]
        )

    browser.close()
