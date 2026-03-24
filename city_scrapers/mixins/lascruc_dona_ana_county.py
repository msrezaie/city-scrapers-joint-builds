import re
from datetime import date, datetime
from zoneinfo import ZoneInfo

import scrapy
from city_scrapers_core.constants import BOARD, COMMISSION, COMMITTEE, NOT_CLASSIFIED
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from dateutil.relativedelta import relativedelta


class LascrucDonaAnaCountySpiderMeta(type):
    """
    Metaclass that enforces required static variables on child spiders.
    """

    def __init__(cls, name, bases, dct):
        if name == "LascrucDonaAnaCountySpiderMixin":
            super().__init__(name, bases, dct)
            return

        if any(
            getattr(base, "__name__", "") == "LascrucDonaAnaCountySpiderMixin"
            for base in bases
        ):
            required_static_vars = ["agency", "name"]
            missing_vars = [var for var in required_static_vars if var not in dct]

            if missing_vars:
                missing_vars_str = ", ".join(missing_vars)
                raise NotImplementedError(
                    f"{name} must define the following static variable(s): "
                    f"{missing_vars_str}."
                )

        super().__init__(name, bases, dct)


class LascrucDonaAnaCountySpiderMixin(
    CityScrapersSpider, metaclass=LascrucDonaAnaCountySpiderMeta
):
    agency = None
    timezone = "America/Denver"
    api_base_url = "https://donaanaconm.api.civicclerk.com"
    portal_base_url = "https://donaanaconm.portal.civicclerk.com"
    custom_settings = {
        "ROBOTSTXT_OBEY": False,
    }

    # Default location - consistent across all WYCOKCK meetings
    location_name = "Dona Ana County"
    default_address = "845 N Motel Blvd, Las Cruces, NM 88007"

    # Date range configuration (can be overridden by subclasses)
    # First meeting in CivicClerk API: 2015-05-04
    start_date_str = "2020-01-01"
    months_ahead = 12

    def start_requests(self):
        """Generate API requests for past and upcoming events."""
        if hasattr(self, "compliance_url"):
            yield scrapy.Request(self.compliance_url, callback=self.parse_compliance)
            # print(f"Compliance URL found for {self.name}: {self.compliance_url}")
            return
        else:
            # yield scrapy.Request(self.compliance_url, callback=self.parse_compliance)
            # today = datetime.now(timezone.utc)
            today = datetime.now(tz=ZoneInfo(self.timezone))

            start_date = date.fromisoformat(self.start_date_str)
            end_date = today + relativedelta(months=self.months_ahead)

            start_date_str = start_date.isoformat()
            end_date_str = end_date.isoformat()
            today_str = today.isoformat()

            ids_str = self.category_id
            category_filter = f"categoryId+in+({ids_str})"

            urls = [
                # Past events (from start_date to today)
                f"{self.api_base_url}/v1/Events?$filter=startDateTime+ge+{start_date_str}+and+startDateTime+lt+{today_str}+and+{category_filter}&$orderby=startDateTime+desc,+eventName+desc",  # noqa
                # Upcoming events (today to end_date)
                f"{self.api_base_url}/v1/Events?$filter=startDateTime+ge+{today_str}+and+startDateTime+le+{end_date_str}+and+{category_filter}&$orderby=startDateTime+asc,+eventName+asc",  # noqa
            ]
            for url in urls:
                yield scrapy.Request(url, callback=self.parse)

    def parse_compliance(self, response):
        compliance_meeting = response.css("ul.file-group li a::attr(href)").get()
        print("HERE", compliance_meeting)
        pass

    def parse(self, response):
        """
        Parse JSON response from CivicClerk API and yield Meeting items.
        """
        data = response.json()
        events = data.get("value", [])

        for raw_event in events:
            event_id = raw_event.get("id")
            if not event_id:
                continue

            raw_title = raw_event.get("eventName") or self.agency
            title = self._parse_title(raw_title)
            meeting = Meeting(
                title=title,
                description=raw_event.get("eventDescription") or "",
                classification=self._parse_classification(f"{title} {self.agency}"),
                start=self._parse_start(raw_event),
                end=self._parse_end(raw_event),
                all_day=False,
                time_notes="",
                location=self._parse_location(raw_event),
                links=self._parse_links(raw_event),
                source=f"{self.portal_base_url}/event/{event_id}",
            )
            meeting["status"] = self._get_status(meeting, text=raw_title)
            meeting["id"] = self._get_id(meeting)

            yield meeting

        # Handle pagination
        next_link = data.get("@odata.nextLink")
        if next_link:
            yield scrapy.Request(next_link, callback=self.parse)

    def _parse_classification(self, title):
        """
        Parse classification from meeting title and agency name.
        """
        classification_map = {
            "commission": COMMISSION,
            "board": BOARD,
            "committee": COMMITTEE,
        }

        for keyword, classification in classification_map.items():
            if keyword in title.lower():
                return classification

        return NOT_CLASSIFIED

    def _parse_title(self, raw_title):
        """
        Parse or generate meeting title with robust normalization.

        Removes:
        - Any trailing parenthetical content: "Title (anything)" -> "Title"
        - Leading dates: "8.15.24 Title" -> "Title"
        - Trailing dates: "Title 01.28.26" -> "Title"
        - Extra whitespace
        """
        title = raw_title
        # 10/07/2021
        # (6/25/21)
        # March 10, 2026
        # 13 Oct 22
        # remove ONLY from the start:
        # start_date_pattern = r'^\s*\(?\s*(?:\d{1,2}\s*/\s*\d{1,2}\s*/\s*\d{2,4}|\d{1,2}\s+[A-Za-z]{3,9}\s+\d{2,4})\s*\)?\s*' # noqa

        end_date_pattern = r"\s*(?:\d{1,2}\s*/\s*\d{1,2}\s*/\s*\d{2,4}|\d{1,2}\s+[A-Za-z]{3,9}\s+\d{2,4}|[A-Za-z]{3,9}\s+\d{1,2},\s+\d{2,4})\s*$"  # noqa
        # title = re.sub(start_date_pattern, "", title)
        title = re.sub(end_date_pattern, "", title)
        # # Remove any parenthetical content at end of string
        # title = re.sub(r"\s*\([^)]*\)\s*$", "", title)
        # # Remove leading dates (8.15.24, 10.12.23)
        # title = re.sub(r"^\d{1,2}[//]\d{1,2}[//]\d{2,4}\s+", "", title)
        # # Remove trailing dates in various formats (01.28.26, 01/28/2026, etc.)
        # title = re.sub(r"\s+\d{1,2}[./]\d{1,2}[./]\d{2,4}\s*$", "", title)
        # # Collapse multiple spaces to single space
        # title = re.sub(r"\s+", " ", title).strip()
        return title

    def _parse_start(self, raw_event):
        """Parse start datetime as a naive datetime object."""
        start_str = raw_event.get("startDateTime")
        return self._parse_dt(start_str)

    def _parse_end(self, raw_event):
        """Parse end datetime as a naive datetime object. Added by pipeline if None"""
        end_str = raw_event.get("endDateTime")
        return self._parse_dt(end_str)

    def _parse_location(self, raw_event):
        """Parse or generate location."""
        event_location = raw_event.get("eventLocation") or {}

        address_parts = [
            event_location.get("address1") or "",
            event_location.get("address2") or "",
            ", ".join(
                part
                for part in [
                    event_location.get("city"),
                    event_location.get("state"),
                    event_location.get("zipCode"),
                ]
                if part
            ),
        ]
        address = " ".join(part for part in address_parts if part).strip()

        # Default address if none provided in the event
        if not address:
            address = self.default_address

        return {
            "name": self.location_name,
            "address": address,
        }

    def _parse_links(self, raw_event):
        """Parse or generate links."""
        event_id = raw_event.get("id")
        links = []
        for f in raw_event.get("publishedFiles", []):
            file_id = f.get("fileId")
            if not file_id or not event_id:
                continue
            links.append(
                {
                    "title": f.get("type") or "Document",
                    "href": f"{self.portal_base_url}/event/{event_id}/files/agenda/{file_id}",  # noqa
                }
            )
        return links

    def _parse_dt(self, dt_str):
        """Parse an ISO datetime string into a naive datetime object."""
        if not dt_str:
            return None
        # Handle ISO format like '2025-11-19T11:30:00Z'
        dt_str = dt_str.replace("Z", "+00:00")
        try:
            dt = datetime.fromisoformat(dt_str)
            # Return naive datetime (strip timezone)
            return dt.replace(tzinfo=None)
        except ValueError:
            return None
