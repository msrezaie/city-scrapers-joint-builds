from city_scrapers_core.spiders import CityScrapersSpider


class AtlSouthFultonCityCouncilSpiderMeta(type):
    """
    Metaclass that enforces required static variables on child spiders.
    """

    def __init__(cls, name, bases, dct):
        if name == "AtlSouthFultonCityCouncilSpiderMixin":
            super().__init__(name, bases, dct)
            return

        if any(
            getattr(base, "__name__", "") == "AtlSouthFultonCityCouncilSpiderMixin"
            for base in bases
        ):
            required_static_vars = ["agency", "name", "id"]
            missing_vars = [var for var in required_static_vars if var not in dct]

            if missing_vars:
                missing_vars_str = ", ".join(missing_vars)
                raise NotImplementedError(
                    f"{name} must define the following static variable(s): "
                    f"{missing_vars_str}."
                )

        super().__init__(name, bases, dct)


class AtlSouthFultonCityCouncilSpiderMixin(
    CityScrapersSpider, metaclass=AtlSouthFultonCityCouncilSpiderMeta
):
    """
    Base mixin for South Fulton NovusAgenda spiders.
    """

    name = None
    agency = None
    id = None

    timezone = "America/New_York"
    start_urls = [
        "https://southfulton.novusagenda.com/agendapublic/meetingsresponsive.aspx"
    ]

    def parse(self, response):
        """
        Main parse method.
        """
        pass

    def _parse_meeting(self, item, response=None):
        """
        Parse one meeting item and return a Meeting or None.
        """
        pass

    def _parse_title(self, item):
        pass

    def _parse_description(self, item):
        pass

    def _parse_classification(self, item):
        pass

    def _parse_start(self, item):
        pass

    def _parse_end(self, item):
        pass

    def _parse_all_day(self, item):
        pass

    def _parse_time_notes(self, item):
        pass

    def _parse_location(self, item):
        pass

    def _parse_links(self, item):
        pass

    def _parse_source(self, item=None, response=None):
        pass

    def _parse_status(self, meeting, item=None):
        return self._get_status(meeting)

    def _dedupe_links(self, links):
        seen = set()
        deduped = []

        for link in links:
            link_tuple = (link["href"], link["title"])
            if link_tuple not in seen:
                seen.add(link_tuple)
                deduped.append(link)

        return deduped