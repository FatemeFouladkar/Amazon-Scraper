import scrapy
import datetime

class PhoneSpider(scrapy.Spider):
    name = 'phone'
    allowed_domains = ['amazon.com']
    start_urls = ['http://amazon.com/']

    custom_settings = {
        'CONCURRENT_REQUESTS': 2,
        'DOWNLOAD_DELAY': 2,
        'RETRY_TIMES': 5,
        'FEED_URI': f'outputs/phones_{datetime.datetime.today().strftime("%d-%m-%Y")}.csv',
        'FEED_FORMAT': 'csv',
        'FEED_EXPORT_FIELDS': [ 'title', 'link','price', 'rating',\
                                'brand', 'model_name', 'operating_system',\
                                'cellular_technology', 'wireless_network_technology', 'about']
        }

    def __init__(self, name=None, **kwargs):
        super().__init__(name, **kwargs)
        self.input_urls = self.get_links_from_file('input/input links.txt')

    
    def start_requests(self):
        for url in self.input_urls:
            yield scrapy.Request(url, callback=self.parse)


    def parse(self, response):
        product_links = response.xpath("//a[@class='a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal']/@href").getall()
        for link in product_links :
            yield response.follow(link, callback=self.parse_product)

        next_page = response.xpath("//a[@class='s-pagination-item s-pagination-next s-pagination-button s-pagination-separator']/@href").get()
        while next_page:
            yield response.follow(next_page, callback=self.parse)


    def parse_product(self, response):
        link = response.url
        title = response.xpath("//span[@id='productTitle']/text()").get().strip()
        price = response.xpath("//span[@class='a-price aok-align-center reinventPricePriceToPayMargin priceToPay']/span/text()").get()
        rating = response.xpath("//i[contains(@class,'a-icon a-icon-star')]/span/text()").get().split(' ')[0]
        brand = response.xpath("//table[@class='a-normal a-spacing-micro']/tr[@class='a-spacing-small po-brand']/td[@class='a-span9']/span/text()").get()
        model_name = response.xpath("//table[@class='a-normal a-spacing-micro']/tr[@class='a-spacing-small po-model_name']/td[@class='a-span9']/span/text()").get()
        operating_system = response.xpath("//table[@class='a-normal a-spacing-micro']/tr[@class='a-spacing-small po-operating_system']/td[@class='a-span9']/span/text()").get()
        cellular_technology = response.xpath("//table[@class='a-normal a-spacing-micro']/tr[@class='a-spacing-small po-cellular_technology']/td[@class='a-span9']/span/text()").get()
        wireless_network_technology = response.xpath("//table[@class='a-normal a-spacing-micro']/tr[@class='a-spacing-small po-wireless_network_technology']/td[@class='a-span9']/span/text()").get()
        about = ' '.join(response.xpath("//div[@id='feature-bullets']/ul/li/span/text()").getall()).strip()
        
        yield {
            'title': title,
            'link': link,
            'price': price if price else response.xpath("//table[@class='a-lineitem a-align-top']/tr/td[@class='a-span12']/span/span/text()").get(),
            'rating': rating,
            'brand': brand,
            'model_name': model_name,
            'operating_system': operating_system,
            'cellular_technology': cellular_technology,
            'wireless_network_technology': wireless_network_technology,
            'about': about,
        }


    def get_links_from_file(self, filename):
        with open(filename, mode='r', encoding='utf-8') as links:
            return [str(link).strip() for link in links.readlines()]
