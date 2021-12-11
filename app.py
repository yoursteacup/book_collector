import requests
import json
import time
import logging
from random import randint
from lxml import etree, html
from urllib.parse import urlparse
from fp.fp import FreeProxy

logging.getLogger("requests").setLevel(logging.CRITICAL)
parser = etree.HTMLParser()
sources_prefs = json.load(open("sources.json", "r"))
user_agents = json.load(open("user_agents.json", "r"))["user_agents"]
headers = {
	"Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
	"Accept-Encoding": "gzip, deflate",
	"Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7"
}
no_proxy_response = "There are no working proxies at this time."

def getProxy():
	proxies = {}
	proxy = no_proxy_response
	while proxy == no_proxy_response or proxy == None:
		proxy = FreeProxy(rand=True).get()
		if proxy == no_proxy_response:
			print("No proxy returned. Sleeping for 1 second...")
			time.sleep(1)
	print(f"Fetching with proxy: {proxy}")
	proxies["http"] = proxy
	return proxies

def getPage(fetched_page, content_element, page_number_element):
	tree = html.fromstring(fetched_page.content)
	page = {}
	text = ""
	for element in tree.xpath(content_element):
		text += element.text_content()
	page[tree.xpath(page_number_element)[0].text_content()] = text
	return page

def bookNotReady(pages_got, pages_fetched):
	for page in pages_got:
		if page not in pages_fetched:
			return True
	return False

def fetchPage(url, headers, proxies):
	# return requests.get(url, allow_redirects = True, headers = headers, proxies = proxies)
	return requests.get(url, allow_redirects = True, headers = headers)

def getPageLinks(domain, tree, navigation_button):
	pages_got = []
	for element in tree.xpath(navigation_button):
		url = element.attrib["href"]
		if f"http://{domain}" not in url:
			url = f"http://{domain}/{url}"
		else:
			url = page
		pages_got.append(url)
	return pages_got

def getBook(url):
	domain = urlparse(url).netloc
	if domain in sources_prefs:
		# proxies = getProxy()
		proxies = {}
		headers["User-Agent"] = user_agents[randint(0, len(user_agents) - 1)]
		print(headers["User-Agent"])
		fetched_page = fetchPage(url, headers, proxies)
		tree = html.fromstring(fetched_page.content)
		current_pref = sources_prefs[domain]

		title = tree.xpath(current_pref["title"])[0].text_content()
		print(f"Book title: {title}")
		pages = []
		page_count = 1
		if current_pref["navigation"]["type"] == "pages":
			navigation_button = current_pref["navigation"]["element"]
			pages_got = []
			pages_fetched = []
			pages.append(getPage(fetched_page, current_pref["content"], current_pref["page_number"]))
			pages_fetched.append(url)
			pages_got = getPageLinks(domain, tree, navigation_button)

			while bookNotReady(pages_got, pages_fetched):
				for page in pages_got:
					if page not in pages_fetched:
						time.sleep(1)
						if f"http://{domain}" not in page:
							url = f"http://{domain}/{page}"
						else:
							url = page
						pages_fetched.append(url)
						fetched_page = fetchPage(url, headers, proxies)
						tree = html.fromstring(fetched_page.content)
						for element in tree.xpath(navigation_button):
							if url not in pages_fetched:
								pages_got.append(url)
						print(fetched_page)
						pages.append(getPage(fetched_page, current_pref["content"], current_pref["page_number"]))
						page_count += 1
						for fresh_page in getPageLinks(domain, tree, navigation_button):
							if fresh_page not in pages_got:
								pages_got.append(fresh_page)

			book = {}
			book["title"] = title
			book["pages"] = pages
			book["page_count"] = page_count
			return book
		else:
			return None
	else:
		print(f"Domain {domain} is not yet set up!")
		return None

def writeBook(book):
	with open(f"{book['title']}.txt", "a", encoding = "utf-8") as openedBook: 
		for x in range(book["page_count"] + 1):
			for page in book["pages"]:
				if str(x) in page:
					openedBook.write(page[str(x)])
		openedBook.close()

if __name__ == "__main__":
	url = "http://loveread.me/read_book.php?id=4370&p=1"
	writeBook(getBook(url))