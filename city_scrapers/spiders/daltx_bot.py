from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from city_scrapers_core.constants import NOT_CLASSIFIED
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
import scrapy


class DaltxBotSpider(CityScrapersSpider):
    name = "daltx_bot"
    agency = "Dallas College Board of Trustees"
    timezone = "America/Chicago"
    start_url = "https://www.dallascollege.edu/events/?categories%5B%5D=Category%3EBoard%20of%20Trustees&search=all"

    videos_endpoint = "https://mediaportal.dallascollege.edu/api/v1.0/media?Count=190&Offset=0&Type=Video&Privacy=Public&Edate={end_date}&Bdate={start_date}"
    tz=ZoneInfo(timezone)
    def start_requests(self):
        start_date = datetime.now(tz=self.tz) - timedelta(days=365 * 3)
        end_date = datetime.now(tz=self.tz) + timedelta(days=365)
        
        yield scrapy.Request(
            self.videos_endpoint.format(start_date=start_date.strftime("%Y-%m-%d"), end_date=end_date.strftime("%Y-%m-%d")
            ),
            callback=self.parse
        )
    def parse(self, response):
        videos_meta = response
        data = response.json()
        # print(f"DATA: {data}")
        print(len(data["items"]))
        yield scrapy.Request(
            url = self.start_url,
            meta = {"videos_meta": videos_meta},
            callback=self.parse_records
        )
    def parse_records(self, response):
        records = response.css(".row.calendar-search-results").getall()
        print(len(records))
        # for record in records:
            # print(f"HERE: {record}")
            # meeting = Meeting(
            #     title=self._parse_title(item),
            #     description=self._parse_description(item),
            #     classification=self._parse_classification(item),
            #     start=self._parse_start(item),
            #     end=self._parse_end(item),
            #     all_day=self._parse_all_day(item),
            #     time_notes=self._parse_time_notes(item),
            #     location=self._parse_location(item),
            #     links=self._parse_links(item),
            #     source=self._parse_source(response),
            # )

            # meeting["status"] = self._get_status(meeting)
            # meeting["id"] = self._get_id(meeting)

            # yield meeting

    def _parse_title(self, item):
        """Parse or generate meeting title."""
        return ""

    def _parse_description(self, item):
        """Parse or generate meeting description."""
        return ""

    def _parse_classification(self, item):
        """Parse or generate classification from allowed options."""
        return NOT_CLASSIFIED

    def _parse_start(self, item):
        """Parse start datetime as a naive datetime object."""
        return None

    def _parse_end(self, item):
        """Parse end datetime as a naive datetime object. Added by pipeline if None"""
        return None

    def _parse_time_notes(self, item):
        """Parse any additional notes on the timing of the meeting"""
        return ""

    def _parse_all_day(self, item):
        """Parse or generate all-day status. Defaults to False."""
        return False

    def _parse_location(self, item):
        """Parse or generate location."""
        return {
            "address": "",
            "name": "",
        }

    def _parse_links(self, item):
        """Parse or generate links."""
        return [{"href": "", "title": ""}]

    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url
