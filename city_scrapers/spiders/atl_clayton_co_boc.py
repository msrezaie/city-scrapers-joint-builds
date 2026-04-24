import scrapy
from zoneinfo import ZoneInfo
from datetime import datetime
from dateutil.parser import parse as dateparser
from city_scrapers_core.constants import BOARD, NOT_CLASSIFIED
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class AtlClaytonCoBocSpider(CityScrapersSpider):
    name = "atl_clayton_co_boc"
    agency = "Clayton County Board of Commissioners"
    timezone = "America/Chicago"
    source_url = "https://claytoncountyga.primegov.com/public/portal?fromiframe=true"
    api_url = "https://claytoncountyga.primegov.com/api/v2/PublicPortal/ListArchivedMeetings?year={year}"
    attachment_url = "https://claytoncountyga.primegov.com/Public/CompiledDocument?meetingTemplateId={template_id}&compileOutputType=1"
    html_url = "https://claytoncountyga.primegov.com/Portal/Meeting?meetingTemplateId={template_id}"

    custom_settings = {
        "ROBOTSTXT_OBEY": False,
    }

    def start_requests(self):
        current_year = datetime.now(ZoneInfo(self.timezone)).year
        for year in range(current_year - 3, current_year + 1):
            yield scrapy.Request(
                url=self.api_url.format(year=year),
                callback=self.parse,
                )
    def parse(self, response):
        response = response.json()
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        for item in response:
            meeting = Meeting(
                title=self._parse_title(item),
                description="",
                classification=BOARD,
                start=self._parse_start(item),
                end=None,
                all_day=False,
                time_notes="",
                location=self._parse_location(item),
                links=self._parse_links(item),
                source=self.source_url,
            )

            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)
            yield meeting
    def _parse_title(self, item):
        """Parse or generate meeting title."""

        return item.get("title", "")

    def _parse_start(self, item):
        """Parse start datetime as a naive datetime object."""
        date = item.get("date", "")
        time = item.get("time", "")
        parsed_start = None
        if date and time:
            dt_str = f"{date} {time}"
            parsed_start = dateparser(dt_str)
        elif date:
            parsed_start = dateparser(date)

        return parsed_start

    def _parse_location(self, item):
        """Parse or generate location."""
        return {
            "address": "",
            "name": "",
        }

    def _parse_links(self, item):
        """Parse or generate links."""
        links = []

        parsed_links = item.get("documentList", [])
        parsed_video_links = item.get("videoUrl", "")

        for link in parsed_links:
            if "HTML Agenda" in link.get("templateName", ""):
                href_link = self.html_url.format(template_id=link.get("templateId", "")),
            else:
                 href_link = self.attachment_url.format(template_id=link.get("templateId", ""))

            links.append({
                 "title": link.get("templateName", ""),
                 "href": href_link,
               
            })

        if parsed_video_links:

            links.append({
                "title": "Video",
                "href": "https:" + parsed_video_links if not "https:" in parsed_video_links else parsed_video_links,
                
            })
        return links

