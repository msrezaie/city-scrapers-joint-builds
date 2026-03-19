from city_scrapers.mixins.lascruc_dona_ana_county import SpiderFactoryTemplateMixin


# list of agencies
# "BOCC Agendas" id = 28
# "Planning and Zoning" id = 27
# "Labor Management Relations" = id 30
# "Airport Advisory Board" id = 31
# "Development Review Committee" id = 29
# "County ADA Advisory Board" id = 26
# "Compliance Office" id = https://www.donaana.gov/government/agendas/compliance_office.php
spider_configs = [
    {}
]

def create_spiders():
    """
    Dynamically create spider classes using the spider_configs list
    and register them in the global namespace.
    """
    for config in spider_configs:
        class_name = config["class_name"]

        if class_name not in globals():
            # Build attributes dict without class_name to avoid duplication.
            # We make sure that the class_name is not already in the global namespace
            # Because some scrapy CLI commands like `scrapy list` will inadvertently
            # declare the spider class more than once otherwise
            attrs = {k: v for k, v in config.items() if k != "class_name"}

            # Dynamically create the spider class
            spider_class = type(
                class_name,
                (SpiderFactoryTemplateMixin,),
                attrs,
            )

            globals()[class_name] = spider_class


# Create all spider classes at module load
create_spiders()
