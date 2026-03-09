from urllib import response
from city_scrapers_core.constants import NOT_CLASSIFIED
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from datetime import time, datetime
import scrapy
from dateutil.parser import parse as dateparser


class IlRegionalTransitSpider(CityScrapersSpider):
    name = "il_regional_transit"
    agency = "Regional Transportation Authority"
    timezone = "America/Chicago"
    all_meetings_url = "https://www.rtachicago.org/about-rta/boards-and-committees/meeting-materials?year={year}" # noqa
    upcoming_meetings_url = "https://www.rtachicago.org/about-rta/boards-and-committees/meeting-materials" # noqa

    _location = {
        "name": "RTA Headquarters",
        "address": "175 W. Jackson Blvd., Chicago, IL 60604",
    }

    _time_note = "Check the source link for the most up-to-date information on meeting times and locations." # noqa

    _start_time = time(9, 0)

    custom_settings = {"ROBOTSTXT_OBEY": False}

    def start_requests(self):
        yield scrapy.Request(
            url=self.upcoming_meetings_url,
            callback=self._get_all_meetings,
        )

    def _get_all_meetings(self, response):
        upcoming_section = response.css(".bg-rtadarkgray-500.w-full.grid.grid-cols-1.p-8.mb-12.border-t-4.border-rtayellow-500") # noqa
        current_year = datetime.now().year
        for year in range(current_year - 5, current_year + 1):
            yield scrapy.Request(
                url=self.all_meetings_url.format(year=year),
                callback=self.parse,
                meta={"upcoming_section": upcoming_section},
            )
            break

    def parse(self, response):
        upcoming_section = response.meta.get("upcoming_section")
        meetings = response.css(".grid.grid-cols-1")[0]
        upcoming_data = upcoming_section.css(".bg-rtadarkgray-500.w-full.grid.grid-cols-1.p-8.mb-12.border-t-4.border-rtayellow-500")
        archived_data = meetings.css(".bg-rtadarkgray-500.border-t-4.border-rtayellow-500.p-6").getall()

        upcoming_meetings = self._parse_upcoming_meetings(upcoming_data)
        # archived_meetings = self._parse_archived_meetings(archived_data)

        # meetings = upcoming_meetings + archived_meetings
        print(upcoming_meetings)

        # for item in meetings:
        #     meeting = Meeting(
        #         title=self._parse_title(item),
        #         description=self._parse_description(item),
        #         classification=self._parse_classification(item),
        #         start=self._parse_start(item),
        #         end=self._parse_end(item),
        #         all_day=self._parse_all_day(item),
        #         time_notes=self._parse_time_notes(item),
        #         location=self._parse_location(item),
        #         links=self._parse_links(item),
        #         source=self._parse_source(response),
        #     )

        #     meeting["status"] = self._get_status(meeting)
        #     meeting["id"] = self._get_id(meeting)

        yield None

    def _parse_upcoming_meetings(self, upcoming_data):
        meetings = []
        location = {
            "name": "",
            "address": "",
        }
        for event in upcoming_data:
            item_location = location.copy()
            title = event.css(".font-heading.text-xl.md\\:text-2xl.text-white.mb-2::text").get()
            start_time = event.css(".text-xl.text-rtayellow-500.mb-4::text").get()
            location_string = event.css("p.text-white.text-sm.mb-4::text").getall()
            links = []

            item_location["name"] = location_string[0].strip() if len(location_string) > 0 else ""
            item_location["address"] = location_string[1].strip() if len(location_string) > 1 else ""

            item = {
                "title": title,
                "start_time": start_time,
                "location": item_location,
                "links": links,
            }

            meetings.append(item)

        return meetings
    
    def _parse_archived_meetings(self, archived_data):
        """Parse archived meetings from the response."""
        # Implement parsing logic for archived meetings
        return []

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
