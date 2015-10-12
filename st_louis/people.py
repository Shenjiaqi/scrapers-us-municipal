from pupa.scrape import Scraper
from pupa.scrape import Person
from lxml import html
import requests

BASE_URL = "https://www.stlouis-mo.gov"
ALDERMEN_HOME = BASE_URL + "/government/departments/aldermen"

# FIXME duplication from StLouis Jurisdiction class in __init__.py
WARD_COUNT = 28

class StLouisPersonScraper(Scraper):

	def scrape(self):
		yield self.scrape_people()

	def scrape_people(self):
		for ward_num in range(1, WARD_COUNT + 1):
			person = self.scrape_alderman(ward_num)
			yield person

	def scrape_alderman(self, ward_num):
		ward_url = "{}/ward-{}".format(ALDERMEN_HOME, ward_num)
		alderman_url = self.alderman_url(ward_url)
		alderman_page = self.lxmlize(alderman_url)

		# person's name is the only <h1> tag on the page
		name = alderman_page.xpath("//h1/text()")[0]

		# initialize person object with appropriate data to tie back to
		# a post in the jurisdiction's "Board of Aldermen" organization
		district = "Ward {} Alderman".format(ward_num)
		person = Person(name=name, district=district, role="Alderman", 
										primary_org="legislature")

		# set additional fields
		person.image = alderman_page.xpath("//div/img/@src")[0]
		phone_number = alderman_page.xpath("//strong[text()='Phone:']/../text()")[1].strip()
		person.add_contact_detail(type="voice", value=phone_number)

		# add sources
		person.add_source(alderman_url, note="profile")
		person.add_source(ward_url, note="ward")

		return person

	def alderman_url(self, ward_url):
		ward_page = self.lxmlize(ward_url)
		# each ward page contains a link to the current alderman's profile.
		# the text of the link says "Email <Jane Doe>" where Jane Doe is the
		# name of the alderman.
		# find that link by selecting for <a> tags whose text contains 'Email'
		return ward_page.xpath("//a[contains(text(), 'Email')]//@href")[0]

	def lxmlize(self, url):
		entry = requests.get(url)
		page = html.fromstring(entry.text)
		page.make_links_absolute(url)
		return page