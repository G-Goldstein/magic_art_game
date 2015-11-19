import urllib.request
import re

def all_matches_from_page(page, regex):
	content = urllib.request.urlopen(page).read().decode('utf-8', 'ignore')
	return re.findall(regex, content)