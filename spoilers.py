import regex
import json
import os
import time
from post import slack_bot

def spoiler_page_html(set):
	matches = regex.all_matches_from_page(spoiler_page(set), 'cards/[^\s]*\.jpg')
	return matches

def spoiler_page(set):
	return 'http://mythicspoiler.com/{!s}/'.format(set)

def get_bot(live=False):
	try:
		with open('magic_art_game.settings') as config:
			settings = json.loads(config.read())
	except:
		# No local settings file, so maybe we're running on OpenShift.
		settings = {
			'magic_channel_url': os.environ['magic_channel_url'],
			'magic_channel_name': os.environ['magic_channel_name'],
			'magic_bot_name': os.environ['magic_bot_name'],
			'magic_bot_icon': os.environ['magic_bot_icon']
		}
	bot = slack_bot(settings['magic_channel_url'], settings['magic_channel_name'], settings['magic_bot_name'], settings['magic_bot_icon'], live)
	return bot

def main(set):
	slack_bot = get_bot(True)
	while True:
		try:
			spoiled = []
			new_spoilers = 0
			spoiled_file = '{!s}.spoiled'.format(set)
			try:
				with open(spoiled_file) as file:
					spoiled = json.loads(file.read())
			except:
				pass
			spoilers = spoiler_page_html(set)
			for spoiler in spoilers:
				if spoiler not in spoiled:
					image_url = '{!s}{!s}'.format(spoiler_page(set), spoiler)
					slack_bot.post_image(image_url, 'New {!s} spoiler'.format(set))
					spoiled.append(spoiler)
					new_spoilers += 1
			if new_spoilers == 0:
				print('No new spoilers right now')
			with open(spoiled_file, 'w') as file:
				file.write(json.dumps(spoiled))
			time.sleep(60)
		except:
			print('Failed to find the spoilers right now')

if __name__ == "__main__":
	try:
		main(os.environ['new_magic_set'])
	except:
		main('ogw')