from city_scrapers.mixins.atl_south_fulton_city_council import (
    AtlSouthFultonCityCouncilSpiderMixin,
)

spider_configs = [
    {
        "class_name": "AltSouthFultonCityCouncilSpider",
        "name": "alt_south_fulton_city_council",
        "agency": "Alt South Fulton City Council",
        "category_id": "26",
    },
    {
        "class_name": "AltSouthFultonGeneralSpider",
        "name": "alt_south_fulton_general",
        "agency": "Alt South Fulton General",
        "category_id": "24",
    },
    {
        "class_name": "AltSouthFultonDowntownDevelopmentAuthoritySpider",
        "name": "alt_south_fulton_downtown_development_authority",
        "agency": "Alt South Fulton Downtown Development Authority",
        "category_id": "27",
    },
    {
        "class_name": "AltSouthFultonConventionandVisitorsBureauSpider",
        "name": "alt_south_fulton_convention_and_visitors_bureau",
        "agency": "Alt South Fulton Convention and Visitors Bureau",
        "category_id": "28",
    },
    {
        "class_name": "AltSouthFultonPlanningCommissionSpider",
        "name": "alt_south_fulton_planning_commission",
        "agency": "Alt South Fulton Planning Commission",
        "category_id": "29",
    },
    {
        "class_name": "AltSouthFultonZoningBoardofAppealsSpider",
        "name": "alt_south_fulton_zoning_board_of_appeals",
        "agency": "Alt South Fulton Zoning Board of Appeals",
        "category_id": "30",
    },
    {
        "class_name": "AltSouthFultonpublicArtsCommitteeSpider",
        "name": "alt_south_fulton_public_arts_committee",
        "agency": "Alt South Fulton Public Arts Committee",
        "category_id": "31",
    },
    {
        "class_name": "AltSouthFultonBoardofCodeEnforcementSpider",
        "name": "alt_south_fulton_board_of_code_enforcement",
        "agency": "Alt South Fulton Board of Code Enforcement",
        "category_id": "32",
    },
    {
        "class_name": "AltSouthFultonHistoricandCulturalLandmarksCommissionSpider",
        "name": "alt_south_fulton_historic_and_cultural_landmarks_commission",
        "agency": "Alt South Fulton Historic and Cultural Landmarks Commission",
        "category_id": "33",
    },
    {
        "class_name": "AltSouthFultonCityManagerReviewandApprovalsSpider",
        "name": "alt_south_fulton_city_manager_review_and_approvals",
        "agency": "Alt South Fulton City Manager Review and Approvals",
        "category_id": "34",
    }
]


def create_spiders():
    """
    Dynamically create spider classes using the spider_configs list
    and register them in the global namespace.
    """
    for config in spider_configs:
        class_name = config["class_name"]

        if class_name not in globals():
            attrs = {k: v for k, v in config.items() if k != "class_name"}

            spider_class = type(
                class_name,
                (AtlSouthFultonCityCouncilSpiderMixin,),
                attrs,
            )

            globals()[class_name] = spider_class


create_spiders()
