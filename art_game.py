import urllib.request
import re
import json
import time
import sys
import os
from post import slack_bot

valid_difficulties = ['standard', 'easy', 'normal', 'hard', 'impossible']

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
				'alert': (os.environ['alert'] == "True")
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

	def get_card_title(self, image_url):
		page_url = self.get_card_page_url(image_url)
		page = urllib.request.urlopen(page_url)
		title = re.search('(?<=<title>)[^<]*', page.read().decode('utf-8', 'ignore')).group(0)
		return title

	def get_card_name(self, image_url):
		name = re.search('^.*(?=\s\()', get_card_title(image_url)).group(0)
		return name

	def get_card_page_url(self, image_url):
		edition = re.search('(?<=en/).*(?=/\d)', image_url).group(0)
		number = re.search('\d*(?=\.jpg)', image_url).group(0)
		page_url = 'http://magiccards.info/{!s}/en/{!s}.html'.format(edition, number)
		return page_url

	def is_this_an_image(self, image_url):
		try:
			page = urllib.request.urlopen(image_url)
			return True
		except:
			return False

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
		self.magic_bot.post_image(image_url, "Magic Art Game: {!s} difficulty".format(self.settings['difficulty']))
		time.sleep(self.settings['time_for_answers'])
		self.magic_bot.post_message(title_with_link)
		return True

	def start_the_game(self):
		if self.settings['alert']:
			channel = '<!channel>'
		else:
			channel = 'channel'
		self.magic_bot.post_message('Starting {!s} {!s} magic art games in this {!s} with {!s} seconds for answers'.format(self.settings['cards_in_game'], self.settings['difficulty'], channel, self.settings['time_for_answers']))
		for x in range(self.settings['cards_in_game']):
			time.sleep(self.settings['time_between_cards'])
			while not self.play_a_round():
				pass
		self.magic_bot.post_message('Thanks for playing!')

def main():
	try:
		game = magic_art_game('magic_art_game.settings', sys.argv[1], sys.argv[2]=="True")
	except:
		try:
			game = magic_art_game('magic_art_game.settings', sys.argv[1], live=False)
		except:
			game = magic_art_game('magic_art_game.settings', live=False)
	
	game.start_the_game()

if __name__ == "__main__":
	main()