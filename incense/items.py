# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field


class IncenseItem(Item):
    title = Field()
    image_link = Field()
    deep_link = Field()
    opt_price = Field()
    drop_price = Field()
    retail_price = Field()
    currency = Field()
    status = Field()
    date_of_parsing = Field()
