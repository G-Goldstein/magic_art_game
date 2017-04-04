import urllib.request
import urllib.parse
import re
import json
import time
import sys
import os
import random
import regex
import itertools
from post import slack_bot

valid_difficulties = ['standard', 'easy', 'normal', 'hard', 'impossible']

difficulty_descriptions = {
	'standard':'All cards from Standard (Type 2) legal editions',
	'easy':'Rare cards from Core Sets',
	'normal':'All cards from Core Sets',
	'hard':'Rare cards from all sets',
	'impossible':'All cards from all sets'
}

people_to_notify = ['<!channel>']

class magic_art_game:
	def __init__(self, settings_file, difficulty='', live=False):
		try:
			with open('magic_art_game.settings') as config:
				self.settings = json.loads(config.read())
		except:
			# No local settings file, so maybe we're running on OpenShift.
			self.settings = {
				'default_difficulty': os.environ['default_difficulty'],
				'magic_channel_url': os.environ['magic_channel_url'],
				'magic_channel_name': os.environ['magic_channel_name'],
				'magic_bot_name': os.environ['magic_bot_name'],
				'magic_bot_icon': os.environ['magic_bot_icon'],
				'cards_in_game': int(os.environ['cards_in_game']),
				'time_for_answers': int(os.environ['time_for_answers']),
				'time_between_cards': int(os.environ['time_between_cards']),
				'alert': os.environ['alert']
			}
		self._set_difficulty(difficulty)
		self.magic_bot = slack_bot(self.settings['magic_channel_url'], self.settings['magic_channel_name'], self.settings['magic_bot_name'], self.settings['magic_bot_icon'], live)

	def _set_difficulty(self, difficulty):
		if difficulty.lower() not in valid_difficulties:
			try:
				self.settings['difficulty'] = valid_difficulties[int(difficulty)]
			except:
				self.settings['difficulty'] = self.settings['default_difficulty']
		else:
			self.settings['difficulty'] = difficulty

	def img_url_from_html(self, html):
		matches = re.search('(?<=")([^\s]*)(?="\salt="Secret")', html)
		return matches.group(0)

	def random_magic_card(self):
		request_url = 'http://magiccards.info/art-{!s}.html'.format(self.settings['difficulty'])
		page = urllib.request.urlopen(request_url)
		img_url = self.img_url_from_html(str(page.read()))
		return img_url

	def get_card_name(self, image_url):
		name = re.search('^.*(?=\s\()', get_card_title(image_url)).group(0)
		return name

	def get_card_page_url(self, image_url):
		edition = re.search('(?<=en/).*(?=/\d)', image_url).group(0)
		number = re.search('\d*(?=\.jpg)', image_url).group(0)
		page_url = 'http://magiccards.info/{!s}/en/{!s}.html'.format(edition, number)
		return page_url

	def notify_people(self):
		notification = ', '.join(people_to_notify)
		self.magic_bot.post_message('Notifying {!s}'.format(notification))

	def play_a_round(self):
		image_url = self.random_magic_card()
		if not self.is_this_an_image(image_url):
			print('magiccards.info gave me a bad image. Skipping...')
			return False
		try:
			card_title = self.get_card_title(image_url)
			card_page_url = self.get_card_page_url(image_url)
			title_with_link = '<{!s}|{!s}>'.format(card_page_url, card_title)
		except:
			print('magiccards.info gave me a bad image. Skipping...')
			return False
		self.magic_bot.post_images([image_url], "Magic Art Game: {!s} difficulty".format(self.settings['difficulty']))
		time.sleep(self.settings['time_for_answers'])
		self.magic_bot.post_message(title_with_link)
		return True

	def start_the_game(self):
		if self.settings['alert'] == "True":
			channel = '<!channel>'
		else:
			channel = 'channel'
		self.magic_bot.post_message('Starting {!s} {!s} magic art games in this {!s} with {!s} seconds for answers'.format(self.settings['cards_in_game'], self.settings['difficulty'], channel, self.settings['time_for_answers']))
		self.magic_bot.post_message('{!s}: {!s}'.format(self.settings['difficulty'], difficulty_descriptions[self.settings['difficulty']]))
		self.notify_people()
		for x in range(self.settings['cards_in_game']):
			time.sleep(self.settings['time_between_cards'])
			while not self.play_a_round():
				pass
		time.sleep(5)
		self.magic_bot.post_message('Thanks for playing!')

	def start_custom_game(self, filter):
		if self.settings['alert'] == "True":
			channel = '<!channel>'
		else:
			channel = 'channel'
		self.magic_bot.post_message('Starting a magic art game in this {} with filter `{}`'.format(channel, filter))
		self.notify_people()
		for card in itertools.islice(random_cards_with_art_from_filter(filter), 0, self.settings['cards_in_game']):
			time.sleep(self.settings['time_between_cards'])
			self.play_a_round_with_card(card)
		self.magic_bot.post_message('Thanks for playing!')

	def play_a_round_with_card(self, card):
		self.magic_bot.post_images([art_link_for_card(card)], "Magic Art Game: custom difficulty")
		time.sleep(self.settings['time_for_answers'])
		self.magic_bot.post_message(card_title_with_link(card))

def card_set(card):
	return regex.first_match_in_string(card, '^.*(?=/)')

def card_set_number(card):
	return regex.first_match_in_string(card, '(?<=/)\d*[ab]*')

def direct_link_to_card(card, site='gatherer'):
	if site == 'gatherer':
		return direct_link_to_card_gatherer(card)
	return direct_link_to_card_magiccards(card)

def direct_link_to_card_magiccards(card):
	return 'http://magiccards.info/{!s}/en/{!s}.html'.format(card_set(card), card_set_number(card))

def card_name(image_url):
	name = re.search('^.*(?=\s\()', card_title(image_url)).group(0)
	return name

def direct_link_to_card_gatherer(card):
		name = card_name(card)
		set_name = card_set_name(card)
		page_url = 'http://gatherer.wizards.com/Pages/Search/Default.aspx?name=+[{}]&set=["{}"]'.format(name, set_name)
		return page_url

def art_link_for_card(card):
	return 'http://magiccards.info/crop/en/{!s}/{!s}.jpg'.format(card_set(card), card_set_number(card))

def card_has_art(card):
	try:
		page = urllib.request.urlopen(art_link_for_card(card))
		return True
	except:
		return False

def card_title(card):
	page = urllib.request.urlopen(direct_link_to_card(card, site='magiccards'))
	title = re.search('(?<=<title>)[^<]*', page.read().decode('utf-8', 'ignore')).group(0)
	return title

def card_set_name(card):
	title = card_title(card)
	return regex.first_match_in_string(title, '(?<=\().*(?=\))')

def random_arrangement_of_numbers(numbers):
	list_of_numbers = list(range(numbers))
	random.shuffle(list_of_numbers)
	return list_of_numbers

def valid_set_filter():
	return ' or '.join(map(lambda set: 'e:{}/en'.format(set), VALID_SETS))

def random_cards_from_filter(filter):
	parsed_filter = urllib.parse.quote_plus(filter)
	url = 'http://magiccards.info/query?q={!s}&v=card&s=cname'.format(parsed_filter)
	if regex.page_contains_regex(url, 'Your\squery\sdid\snot\smatch\sany\scards'):
		raise StopIteration
	try:
		card_count = int(regex.first_match_from_page(url, '(?<=\s\s)\d*(?=\scards)'))
	except:
		card_count = 1
	card_numbers_list = random_arrangement_of_numbers(card_count)
	for number in card_numbers_list:
		card_page_number = int(number / 20 + 1)
		card_number_on_page = number % 20 + 1
		list_url = 'http://magiccards.info/query?q={!s}&s=cname&v=card&p={!s}'.format(parsed_filter, str(card_page_number))
		cards_on_page = regex.all_matches_from_page(list_url, '(?<=info/scans/en/)[^/]*/\d*[ab]*')
		yield cards_on_page[card_number_on_page - 1]

def random_cards_with_art_from_filter(filter):
	filter += ' l:en'
	fails_in_a_row = 0
	for card in random_cards_from_filter(filter):
		if card_has_art(card):
			fails_in_a_row = 0
			yield card
		else:
			fails_in_a_row += 1
			if fails_in_a_row >= 5:
				raise StopIteration

def card_title_with_link(card):
	return '[[!{}]]'.format(card_name(card))
	return '<{!s}|{!s}>'.format(direct_link_to_card(card), card_title(card))

def main():
	try:
		game = magic_art_game('magic_art_game.settings', sys.argv[1], sys.argv[2]=="True")
	except:
		try:
			game = magic_art_game('magic_art_game.settings', sys.argv[1], live=False)
		except:
			game = magic_art_game('magic_art_game.settings', live=False)
	
	game.start_the_game()

def test():
	game = magic_art_game('magic_art_game.settings', live=(sys.argv[2]=="True"))
	game.start_custom_game(sys.argv[1])

if __name__ == "__main__":
	test()