from city_scrapers.mixins.atl_south_fulton_city_council import (
    AtlSouthFultonCityCouncilSpiderMixin,
)

spider_configs = [
    {
        "class_name": "",
        "name": "",
        "agency": "",
        "id": "",
    },
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