import scrapy
import datetime

class PhoneSpider(scrapy.Spider):
    name = 'phone'
    allowed_domains = ['amazon.com']
    start_urls = ['http://amazon.com/']

    custom_settings = {
        'CONCURRENT_REQUESTS': 5,
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
        self.headers = {'accept': 'text/html, */*; q=0.01',
                        'accept-encoding': 'gzip, deflate, br',
                        'accept-language': 'en-US,en;q=0.9,fa;q=0.8',
                        'content-type': 'application/json',
                        'device-memory': '4',
                        'downlink': '0.15',
                        'dpr': '1',
                        'ect': 'slow-2g',
                        'origin': 'https://www.amazon.com',
                        'referer': 'https://www.google.com',
                        'rtt': '3000',
                        'sec-ch-device-memory': '4',
                        'sec-ch-dpr': '1',
                        'sec-ch-ua': '"Not?A_Brand";v="8", "Chromium";v="108", "Microsoft Edge";v="108"',
                        'sec-ch-ua-mobile': '?0',
                        'sec-ch-ua-platform': '"Windows"',
                        'sec-ch-viewport-width': '869',
                        'sec-fetch-dest': 'empty',
                        'sec-fetch-mode': 'cors',
                        'sec-fetch-site': 'same-origin',
                        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36 Edg/108.0.1462.54', 'viewport-width': '869', 'x-requested-with': 'XMLHttpRequest'
                    }        

    def start_requests(self):
        for url in self.input_urls:
            yield scrapy.Request(url, callback=self.parse, headers=self.headers)


    def parse(self, response):
        product_links = response.xpath("//a[@class='a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal']/@href").getall()
        for link in product_links :
            yield response.follow(link, callback=self.parse_product, headers=self.headers)

        next_page = response.xpath("//a[text()='Next']/@href").get()
        if next_page:
            yield scrapy.Request(response.urljoin(next_page), callback=self.parse, headers=self.headers)


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
