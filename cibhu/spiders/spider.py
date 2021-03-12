import json

import scrapy

from scrapy.loader import ItemLoader

from ..items import CibhuItem
from itemloaders.processors import TakeFirst

import requests

urls = ["https://www.cib.hu/aboutUsSectionServlet/?operation=getPressNewsList",
	"https://www.cib.hu/aboutUsSectionServlet/?operation=getPressNewsArchiveList"]

payload = "{\"component\":\"5a0794ce-815e-4993-a739-358c5ed5db92\",\"bankName\":\"CIB\",\"numberLastYears\":\"1\",\"language\":\"\"}"
headers = {
  'Connection': 'keep-alive',
  'Pragma': 'no-cache',
  'Cache-Control': 'no-cache',
  'sec-ch-ua': '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
  'Accept': 'application/json, text/plain, */*',
  'contextPath': '',
  'sec-ch-ua-mobile': '?0',
  'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36',
  'Content-Type': 'application/json',
  'Origin': 'https://www.cib.hu',
  'Sec-Fetch-Site': 'same-origin',
  'Sec-Fetch-Mode': 'cors',
  'Sec-Fetch-Dest': 'empty',
  'Referer': 'https://www.cib.hu/Maganszemelyek/rolunk/sajtoszoba/sajtokozlemenyek.html',
  'Accept-Language': 'en-US,en;q=0.9,bg;q=0.8',
  'Cookie': '_gcl_au=1.1.1143789040.1615558015; _ga=GA1.2.2021156402.1615558016; _gid=GA1.2.1839745024.1615558016; _cs_c=1; WRIgnore=true; cookie_status_bar=accepted; demoFloating=true; gdpr_cookie_consent="necessary,features,marketing"; _gat_UA-129304750-3=1; _gat_UA-129304750-5=1; _cs_cvars=%7B%221%22%3A%5B%22Page%20Type%22%2C%22aboutUsSectionPage%22%5D%2C%222%22%3A%5B%22Page%20Name%22%2C%22CIB%3ACib%20Bank%3AAbout%20Us%3APress%3APress%20Releases%22%5D%2C%223%22%3A%5B%22Intesa%20Bank%22%2C%22CIB%22%5D%2C%224%22%3A%5B%22Site%20Language%22%2C%22Hu%22%5D%2C%225%22%3A%5B%22Site%20Country%22%2C%22Hungary%22%5D%2C%226%22%3A%5B%22Portal%20Section%22%2C%22public%22%5D%2C%227%22%3A%5B%22Visitor%20Type%22%2C%22guest%22%5D%2C%228%22%3A%5B%22Customer%20Segment%22%2C%22Cib%20Bank%22%5D%7D; _cs_id=924ea9bb-a9f3-aa28-f35e-63706fb5ae9b.1615558017.1.1615558056.1615558017.1.1649722017172.Lax.0; _cs_s=3.1; __CT_Data=gpv=3&ckp=tld&dm=cib.hu&apv_17_www56=3&cpv_17_www56=3; JSESSIONID=vic1QaIVOQh4VgjDDQqstIPpcmaM03jNJxNxIr7J; JSESSIONID=vic1QaIVOQh4VgjDDQqstIPpcmaM03jNJxNxIr7J'
}



class CibhuSpider(scrapy.Spider):
	name = 'cibhu'
	start_urls = ['https://www.cib.hu/Maganszemelyek/rolunk/sajtoszoba/sajtokozlemenyek.html']

	def parse(self, response):
		for url in urls:
			data = requests.request("POST", url, headers=headers, data=payload)
			raw_data = json.loads(data.text)
			for item in raw_data:
				date = item['date']
				title = item['title']
				url = item['readMoreLink']
				yield response.follow(url, self.parse_post, cb_kwargs={'date': date, 'title': title})

	def parse_post(self, response, date, title):
		description = response.xpath('//div[@class="cmsTextWrpper section__contentWrapper"]/p//text()[normalize-space()]').getall()
		description = [p.strip() for p in description]
		description = ' '.join(description).strip()

		item = ItemLoader(item=CibhuItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()
