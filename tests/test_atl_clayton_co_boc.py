from datetime import datetime
from os.path import dirname, join

import pytest
import scrapy
from city_scrapers_core.constants import COMMISSION
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.atl_clayton_co_boc import (
    AtlClaytonCoBocSpider,
)


@pytest.fixture(scope="module")
def spider():
    return AtlClaytonCoBocSpider()


@pytest.fixture(scope="module")
def upcoming_meetings_data():
    response = file_response(
        join(
            dirname(__file__),
            "files",
            "atl_clayton_co_boc_upcoming_meetings.json",   

        ),
        url="https://claytoncountyga.primegov.com/api/v2/PublicPortal/ListUpcomingMeetings?_=1777316145702",  # noqa
    )
    return response

@pytest.fixture(scope="module")
def archived_meetings_data():
    return file_response(
        join(
            dirname(__file__),
            "files",
            "atl_clayton_co_boc_archived_meetings.json",
        ),
        url="https://claytoncountyga.primegov.com/api/v2/PublicPortal/ListArchivedMeetings?year=2026&_=1777316145703",  # noqa
    ).json()


@pytest.fixture(scope="module")
def upcoming_meetings_response(
    upcoming_meetings_data
):
    """This is the main response that parse() receives."""
    url = "https://claytoncountyga.primegov.com/api/v2/PublicPortal/ListUpcomingMeetings?_=1777316145702"  # noqa

    request = scrapy.Request(
        url=url,
        meta={
            "upcoming_meetings": upcoming_meetings_data,
        },
    )

    response = file_response(
        join(
            dirname(__file__),
            "files",
            "atl_clayton_co_boc_upcoming_meetings.json",
        ),
        url=url,
    )

    response.request = request

    return response


@pytest.fixture(scope="module")
def parsed_items(spider, upcoming_meetings_response):
    """Parse all meetings with frozen time and proper meta setup."""
    with freeze_time("2026-04-27"):
        items = list(spider.parse(upcoming_meetings_response))

    return items


def test_count(parsed_items):
    assert len(parsed_items) == 2


def test_title(parsed_items):
    assert parsed_items[0]["title"] == "Commissioners Court"


def test_description(parsed_items):
    assert parsed_items[0]["description"] == ""


def test_start(parsed_items):
    assert parsed_items[0]["start"] == datetime(2025, 9, 16, 10, 0)


def test_end(parsed_items):
    assert parsed_items[0]["end"] == datetime(2025, 9, 16, 17, 0)


def test_time_notes(parsed_items):
    assert parsed_items[0]["time_notes"] == ""


def test_id(parsed_items):
    assert (
        parsed_items[0]["id"]
        == "atl_clayton_co_boc/202509161000/x/commissioners_court"
    )


def test_status(parsed_items):
    assert parsed_items[0]["status"] == "passed"


def test_location(parsed_items):
    assert parsed_items[0]["location"] == {
        "name": "Commissioners Court",  # noqa
        "address": "112 Smith Street, Jonesboro, GA 30236",  # noqa
    }


def test_source(parsed_items):
    assert (
        parsed_items[0]["source"]
        == "https://claytoncountyga.primegov.com/Commissioners-Court"  # noqa
    )


def test_links(parsed_items):
    assert parsed_items[0]["links"] == []


def test_classification(parsed_items):
    assert parsed_items[0]["classification"] == COMMISSION


def test_all_day(parsed_items):
    for item in parsed_items:
        assert item["all_day"] is False