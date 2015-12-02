import urllib.request
import re

def all_matches_from_page(page, regex):
	content = urllib.request.urlopen(page).read().decode('utf-8', 'replace')
	return re.findall(regex, content)

def first_match_from_page(page, regex):
	return all_matches_from_page(page, regex)[0]

def page_contains_regex(page, regex):
	return len(all_matches_from_page(page, regex)) > 0

def first_match_in_string(string, regex):
	return re.search(regex, string).group(0)