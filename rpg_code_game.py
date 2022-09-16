import urllib.request
import urllib.parse
import requests
import re
import json
import time
import sys
import os
import random
from post import slack_bot

class rpg_code_game:
	def __init__(self, settings_file, live=False):
		try:
			with open('rpg_code_game.settings') as config:
				self.settings = json.loads(config.read())
		except:
			raise Exception('No rpg_code_game.settings file found.')
			# No local settings file, so maybe we're running on OpenShift.
		self.slack_bot = slack_bot(self.settings['rpg_channel_url'], self.settings['rpg_channel_name'], self.settings['rpg_bot_name'], self.settings['rpg_bot_icon'], live)

	def img_url_from_html(self, html):
		matches = re.search('(?<=")([^\s]*)(?="\salt="Secret")', html)
		return matches.group(0)

	def rpg_program_count(self):
		request_url = 'http://opengrok.jhc.co.uk/source/search?group=BackOffice+f63&full=*&defs=&refs=&path=BAS%2FQRPGLESRC%2F&hist=&type=&si=full'
		response = requests.get(request_url)
		matches = re.search('(?<=<b>)\d*(?=</b>)', response.text)
		return int(matches.group(0))

	def random_rpg_program(self):
		program_number = random.randint(0, self.rpg_program_count()-1)
		request_url = f'http://opengrok.jhc.co.uk/source/s?n=25&start={program_number}&sort=relevancy&q=*&path=BAS%2FQRPGLESRC%2F&group=BackOffice+f63&full'
		response = requests.get(request_url)
		matches = re.search('(?<=>)[^\s]*\.(RPGLE|SQLRPGLE)', response.text)
		return matches.group(0)

	def page_source_for_program(self, program):
		request_url = self.program_source_url(program)
		response = requests.get(request_url)
		return response.text

	def program_source_url(self, program):
		return 'http://opengrok.jhc.co.uk/source/xref/bitbucket-backoffice-f63/BAS/QRPGLESRC/{!s}'.format(urllib.parse.quote_plus(program))

	def program_lines(self, program):
		lines = re.findall('(?<!F63</a>)(?<=\d</a>)(?!<)[^<]*',self.page_source_for_program(program))
		return lines

	def random_consecutive_elements_from_array(self, array, elements):
		if len(array) <= elements:
			return array
		else:
			start_position = random.randint(0, len(array)-elements)
			return array[start_position:start_position + elements]

	def random_lines_from_program(self, program, lines):
		return self.random_consecutive_elements_from_array(self.program_lines(program), lines)

	def program_title(self, program):
		matches = re.search('.*(?=\.[^\.]*$)', program)
		return matches.group(0)

	def play_a_round(self):
		try:
			program = self.random_rpg_program()
			if program[0] == '@':
				print('Got after program {!s}. Retrying...'.format(program))
				return False
		except Exception as e:
			print(e)
			print('Failed to get a random program. Retrying...')
			return False
		try:
			program_title = self.program_title(program)
			page_source = self.program_source_url(program)
			title_with_link = '<{!s}|{!s}>'.format(page_source, program_title)
			lines = self.random_lines_from_program(program, self.settings['max_lines'])
			message = str(''.join(lines))
		except:
			print(error)
			print('Failed to get the source for program {!s}'.format(program_title))
			return False
		self.slack_bot.post_message('```' + message + '```')
		time.sleep(self.settings['time_for_answers'])
		self.slack_bot.post_message('That was: {!s}'.format(title_with_link))
		return True

	def start_the_game(self):
		if self.settings['alert'] == 'True':
			channel = '<!channel>'
		else:
			channel = 'channel'
		self.slack_bot.post_message('Starting {!s} rounds of RPG code guessing game in this {!s} with {!s} seconds for answers'.format(self.settings['cards_in_game'], channel, self.settings['time_for_answers']))
		for x in range(self.settings['cards_in_game']):
			time.sleep(self.settings['time_between_cards'])
			while not self.play_a_round():
				pass
		self.slack_bot.post_message('Thanks for playing!')

def main():
	game = rpg_code_game('rpg_code_game.settings', True)
	game.start_the_game()

if __name__ == "__main__":
	main()
