import re
import scrapy
import logging
from datetime import datetime
from scrapy.crawler import CrawlerProcess
from incense.items import IncenseItem


class ZamorskiepodarkiSpider(scrapy.Spider):
    name = "zamorskiepodarki"
    allowed_domains = ["zamorskiepodarki.com"]
    start_urls = ["https://zamorskiepodarki.com/"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.images, self.pages, self.image_index = {"images": []}, None, None

    def start_requests(self):
        urls = [
            "https://zamorskiepodarki.com/uk/blagovoniya-i-aksessuary/satya/"
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response, **kwargs):
        products = response.xpath("//div[@class='product-layout product-grid']")
        logging.debug("FIRST - %s", self.images)
        for product in products:
            logging.debug("URL - %s", response.url)
            product_link = product.xpath("div[@class='product-thumb']//div[@class='image']/a/@href").get()
            yield scrapy.Request(url=product_link, callback=self._get_image)
        next_page_url = self._next_page_url(response)
        if next_page_url:
            yield scrapy.Request(url=next_page_url, callback=self.parse)

    def _extract_images_link(self, response):
        products = response.xpath("//div[@class='product-layout product-grid']")
        for product in products:
            product_link = product.xpath("div[@class='product-thumb']//div[@class='image']/a/@href").get()
            yield scrapy.Request(url=product_link, callback=self._get_image)

    @staticmethod
    def _next_page_url(response) -> str or None:
        url = None
        next_pages_tag = response.xpath("//ul[@class='pagination']//li[@class='active']/following-sibling::li")
        next_pages_text = next_pages_tag.xpath("./a/text()").get()
        if next_pages_text and next_pages_text.isdigit():
            url = next_pages_tag.xpath("./a/@href").get()
        return url

    def _get_image(self, response):
        prices_data = self._get_prices_data(response)
        general_product_data = self._get_general_product_data(response)
        logging.debug("IMAGE SHOULD BE DOWNLOADED")
        incense_item = IncenseItem({**general_product_data, **prices_data})
        yield incense_item

    @staticmethod
    def _get_general_product_data(response) -> dict:
        deep_link, date_of_parsing, status = response.url, datetime.now(), "NEW"
        image_link = response.xpath("//a[@class='thumbnail']/@href").get()
        title = response.xpath("//a[@class='thumbnail']/@title").get()
        general_product_data = {"deep_link": deep_link, "date_of_parsing": date_of_parsing, "status": status,
                                "image_link": image_link, "title": title}
        return general_product_data

    @staticmethod
    def _get_prices_data(response) -> dict:
        product_div = response.xpath("//div[@id='product']")
        currency = product_div.xpath("..//meta[@itemprop='priceCurrency']//@content").get()
        opt_price = product_div.xpath("..//span[@class='price-new price-opt-new']/b//text()").get()
        opt_price = float(re.search(r"\d+.\d+", opt_price)[0])
        drop_price = round(opt_price * 1.1, 2)
        retail_price = product_div.xpath("..//div[@class='price-detached price-retail']/span//text()").get()
        retail_price = float(re.search(r"\d+.\d+", retail_price)[0])
        prices_data = {"opt_price": opt_price, "drop_price": drop_price, "retail_price": retail_price,
                       "currency": currency}
        return prices_data


if __name__ == "__main__":
    process = CrawlerProcess()
    process.crawl(ZamorskiepodarkiSpider)
    process.start()
