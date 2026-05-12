from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from city_scrapers_core.constants import BOARD
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from dateutil.parser import parse as date_parser
import scrapy


class DaltxBotSpider(CityScrapersSpider):
    name = "daltx_bot"
    agency = "Dallas College Board of Trustees"
    timezone = "America/Chicago"
    start_url = "https://www.dallascollege.edu/events/?categories%5B%5D=Category%3EBoard%20of%20Trustees&search=all"

    tz=ZoneInfo(timezone)

    videos_endpoint = "https://mediaportal.dallascollege.edu/api/v1.0/media?Count=190&Offset=0&Type=Video&Privacy=Public&Edate={end_date}&Bdate={start_date}"
    video_attachment_url = "https://mediaportal.dallascollege.edu/media/{video_id}/"

    def start_requests(self):
        start_date = datetime.now(tz=self.tz) - timedelta(days=365 * 3)
        end_date = datetime.now(tz=self.tz) + timedelta(days=365)
        
        yield scrapy.Request(
            self.videos_endpoint.format(start_date=start_date.strftime("%Y-%m-%d"), end_date=end_date.strftime("%Y-%m-%d")
            ),
            callback=self.request_videos
        )

    def request_videos(self, response):
        video_data = response.json()
        yield scrapy.Request(
            url = self.start_url,
            meta = {"videos_meta": video_data},
            callback=self.parse
        )

    def parse(self, response):
        records = response.css(".row.calendar-search-results")
        video_items = response.meta.get("videos_meta", {}).get("items", [])

        for item in records:
            detail_url = item.css("h4.cal-header a::attr(href)").get()

            yield response.follow(
                url=response.urljoin(detail_url),
                callback=self._construct_meeting,
                meta={"video_items": video_items, "item": item}
            )

    def _construct_meeting(self, response):
        item = response.meta["item"]
        # print(f"Processing meeting:", item)
        # print(f"Response item:", response.text)

        start, end, all_day = self._parse_datetime(item)
        location, time_notes= self._parse_location(response, all_day)
        meeting = Meeting(
            title=self._parse_title(item),
            description=self._parse_description(item),
            classification=BOARD,
            start=start,
            end=end,
            all_day=all_day,
            time_notes=time_notes,
            location=location,
            links=self._parse_links(response),
            source=response.url,

        )

        meeting["status"] = self._get_status(meeting)
        meeting["id"] = self._get_id(meeting)

        yield meeting

    def _parse_title(self, item):
        item_str = item.css("h4.cal-header a::text").get()
        return item_str.strip() if item_str else ""

    def _parse_description(self, item):
        item_str = item.css(".cal-summary p::text").get()
        return item_str.strip() if item_str else ""

    def _parse_datetime(self, item) -> tuple[datetime, datetime, bool]:
        date_list = item.css(".month::text, .day::text, .year::text").getall()
        date_str = " ".join(date_list).strip()

        start_time = item.css(".mb-2 span:nth-child(2)::text").get()
        end_time = item.css(".mb-2 span:nth-child(3)::text").get()
        
        if start_time == "All day":
            return date_parser(f"{date_str}"), date_parser(f"{date_str}"), True

        start_dt = date_parser(f"{date_str} {start_time.strip()}")
        end_dt = date_parser(f"{date_str} {end_time.strip()}")

        return start_dt, end_dt, False

    def _parse_location(self, response, all_day):
        item =response.css('.accordion-body ul li::text').getall()
        if all_day:
            address ={"address": "","name": ""}
            time_notes= item[2].strip() if item else ""
            return address, time_notes
        
        if item and len(item) > 1:
            return{
                "address": item[2].strip(),
                "name": item[1].strip(),
            }, ""
        else:
            return{
                "address": "",
                "name": "",
            }, ""

    def _parse_links(self, item):
        return [{"href": "", "title": ""}]
