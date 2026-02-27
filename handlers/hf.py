import re
import urllib.parse

import aiohttp
import bs4
import markdownify

from .handler import Handler, StorySummary


BASE_URL = "https://www.hentai-foundry.com"
EMPTY_LINES_PATTERN = re.compile(r"\n[\s*]*\n")
REPEATED_WHITESPACE_PATTERN = re.compile(r" {2,}")
CONVERT_TAGS = [
    "a",
    "b",
    "br",
    "em",
    "i",
    "strong",
]
REQUEST_PARAMS = {"enterAgree": 1}


def clean_description(text: str) -> str:
    markdown = markdownify.markdownify(text, convert=CONVERT_TAGS)
    markdown = EMPTY_LINES_PATTERN.sub("\n\n", markdown)
    markdown = REPEATED_WHITESPACE_PATTERN.sub(" ", markdown)
    return markdown


class HFHandler(Handler):

    def __init__(self):
        super().__init__(
            url_pattern=r"www\.hentai-foundry\.com/stories/user/[^/]+/[^/]+/[^/\s]+",
            color="#ff67a2",
            icon_url="https://img.hentai-foundry.com/themes/Dark/favicon.ico",
        )

    async def link_to_summary(self, link: str) -> StorySummary:
        async with aiohttp.ClientSession(raise_for_status=True) as session:
            async with session.get("https://" + link, params=REQUEST_PARAMS) as response:
                if response.status == 200:
                    content = await response.text()
                else:
                    raise ValueError(f"{link}: {response.status} {response.reason}")
                
        soup = bs4.BeautifulSoup(content, features="lxml")
        titlebar = soup.find("div", attrs={"class": "titlebar"})
        title = titlebar.get_text().strip()
        storyinfo = soup.find("td", attrs={"class": "storyInfo"})
        user = storyinfo.find("a")
        user = user.get_text().strip()
        url = urllib.parse.urljoin(BASE_URL, titlebar.find("a").get("href"))
        description = soup.find("td", attrs={"class": "storyDescript"})
        ratings = description.find("div", attrs={"class": "ratings_box"}).find_all("span")
        if ratings:
            ratings = "**" + "**, **".join([r.get_text().strip() for r in ratings]) + "**"
        else:
            ratings = "*none*"
        for div in description.find_all("div"):
            div.decompose()
        description = clean_description(description.decode_contents())

        return StorySummary(
            title=f"'{title}' by {user}",
            description=f"{description}\n\n{ratings}",
            url=url
        )
