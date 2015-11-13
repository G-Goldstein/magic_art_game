import urllib.request
import re
import json
import time
from post import slack_bot

valid_difficulties = ['standard', 'easy', 'normal', 'hard', 'impossible']

class magic_art_game:
	def __init__(self, settings_file):
		with open('magic_art_game.settings') as config:
			self.settings = json.loads(config.read())
		self._set_difficulty()
		self.magic_bot = slack_bot(self.settings['magic_channel_url'], self.settings['magic_channel_name'], self.settings['magic_bot_name'], self.settings['magic_bot_icon'], live=False)

	def _set_difficulty(self):
		if self.settings['default_difficulty'].lower() not in valid_difficulties:
			try:
				self.settings['difficulty'] = valid_difficulties[int(self.settings['default_difficulty'])]
			except:
				self.settings['difficulty'] = valid_difficulties[0]
		else:
			self.settings['difficulty'] = self.settings['default_difficulty']

	def img_url_from_html(self, html):
		matches = re.search('(?<=")([^\s]*)(?="\salt="Secret")', html)
		return matches.group(0)

	def random_magic_card(self):
		request_url = 'http://magiccards.info/art-{!s}.html'.format(self.settings['difficulty'])
		page = urllib.request.urlopen(request_url)
		img_url = self.img_url_from_html(str(page.read()))
		return img_url

	def get_card_title(self, image_url):
		edition = re.search('(?<=en/).*(?=/\d)', image_url).group(0)
		number = re.search('\d*(?=\.jpg)', image_url).group(0)
		page_url = 'http://magiccards.info/{!s}/en/{!s}.html'.format(edition, number)
		page = urllib.request.urlopen(page_url)
		title = re.search('(?<=<title>)[^<]*', str(page.read())).group(0)
		return title

	def get_card_name(self, image_url):
		return re.search('^.*(?=\s\()', get_card_title(image_url)).group(0)


	def play_a_round(self):
		image_url = self.random_magic_card()
		try:
			card_title = self.get_card_title(image_url)
		except:
			print('magiccards.info gave me a bad image. Skipping...')
			return False
		self.magic_bot.post_image(image_url, "Magic Art Game: {!s} difficulty".format(self.settings['difficulty']))
		time.sleep(self.settings['time_for_answers'])
		self.magic_bot.post_message(card_title)
		return True

	def start_the_game(self):
		self.magic_bot.post_message('Starting {!s} {!s} magic art games in this <!channel> with {!s} seconds for answers'.format(self.settings['cards_in_game'], self.settings['default_difficulty'], self.settings['time_for_answers']))
		for x in range(self.settings['cards_in_game']):
			time.sleep(5)
			while not self.play_a_round():
				pass
		self.magic_bot.post_message('Thanks for playing!')

game = magic_art_game('magic_art_game.settings')
game.start_the_game()