import asyncio
import dataclasses
import re

import stoat


@dataclasses.dataclass
class StorySummary:
    title: str
    url: str
    description: str


class Handler:
    url_pattern: re.Pattern
    color: str
    icon_url: str

    def __init__(self, url_pattern: str, color: str, icon_url: str) -> None:
        self.url_pattern = re.compile(url_pattern)
        self.color = color
        self.icon_url = icon_url
    
    def message_to_links(self, message: str) -> list[str]:
        return self.url_pattern.findall(message)
    
    async def link_to_summary(self, link: str) -> StorySummary:
        raise NotImplementedError()

    def summary_to_embed(self, summary: StorySummary) -> stoat.SendableEmbed:
        return stoat.SendableEmbed(
            color=self.color,
            description=summary.description,
            icon_url=self.icon_url,
            title=summary.title,
            url=summary.url,
            media=None
        )

    async def message_to_embeds(self, message: str) -> list[stoat.SendableEmbed]:
        links = self.message_to_links(message)
        summaries = await asyncio.gather(*[self.link_to_summary(link) for link in links])
        return [self.summary_to_embed(summary) for summary in summaries]
