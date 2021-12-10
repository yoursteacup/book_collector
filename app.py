import requests
import json
from random import randint
from lxml import etree, html
from urllib.parse import urlparse
from fp.fp import FreeProxy

parser = etree.HTMLParser()
sources_prefs = json.load(open("sources.json", "r"))
user_agents = json.load(open("user_agents.json", "r"))["user_agents"]
headers = {
	"Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
	"Accept-Encoding": "gzip, deflate",
	"Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7"
}

def get_page(url):
	domain = urlparse(url).netloc
	if domain in sources_prefs:
		proxies = {}
		proxy = FreeProxy(rand=True).get()
		print(proxy)
		proxies["http"] = proxy
		headers["User-Agent"] = user_agents[randint(0, len(user_agents) - 1)]
		fetched_page = requests.get(url, allow_redirects = True, headers = headers, proxies = proxies)
		tree = html.fromstring(fetched_page.content)
		current_pref = sources_prefs[domain]
		title = tree.xpath(current_pref["title"])[0].text_content()
		print(title)
	else:
		print(f"Domain {domain} is not yet set up")

if __name__ == "__main__":


	url = "https://www.tutorialspoint.com/downloading-files-from-web-using-python"
	# r = requests.get(url, allow_redirects=True)
	# open('book.txt', 'wb').write(r.content)
	get_page(url)