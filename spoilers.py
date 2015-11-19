import regex
import json
import os
import time
from post import slack_bot
import post

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
	slack_bot = get_bot(False)
	gone_bad = False
	try:
		data_directory = os.environ['OPENSHIFT_DATA_DIR ']
	except:
		data_directory = 'datablahblah'
	while not gone_bad:
		try:
			spoiled = []
			new_spoilers = 0
			spoiled_file = '{!s}/{!s}.spoiled'.format(data_directory, set)
			post.write_to_log('Data file trying to write to: {!s}'.format(spoiled_file))
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
				post.write_to_log('No new spoilers right now')
			try: 
				with open(spoiled_file, 'w+') as file:
					file.write(json.dumps(spoiled))
			except:
				slack_bot.post_message('I have failed. Dying now.')
				gone_bad = True
		except:
			post.write_to_log('No new spoilers right now')
		if not gone_bad:
			time.sleep(60)

if __name__ == "__main__":
	try:
		set = os.environ['new_magic_set']
	except:
		set = 'ogw'
	main(set)