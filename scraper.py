from playwright.sync_api import sync_playwright
from feedgen.feed import FeedGenerator
from datetime import datetime

sites=[
{"name":"deziiign","url":"https://deziiign.com/","feed":"deziiign.xml"},
{"name":"mediiia","url":"https://mediiia.com/","feed":"mediiia.xml"}
]

with sync_playwright() as p:
    browser=p.chromium.launch()
    page=browser.new_page()

    for s in sites:
        page.goto(s["url"], wait_until="networkidle")

        links=page.locator("a").evaluate_all(
        '''els=>els.map(e=>({
        title:e.innerText,
        href:e.href
        })).filter(x=>x.title&&x.href)'''
        )[:20]

        fg=FeedGenerator()
        fg.title(s["name"])
        fg.link(href=s["url"])
        fg.description(f"Generated feed for {s['name']}")

        for i in links:
            e=fg.add_entry()
            e.title(i["title"])
            e.link(href=i["href"])
            e.guid(i["href"])
            e.pubDate(datetime.utcnow())

        fg.rss_file(s["feed"])

    browser.close()
