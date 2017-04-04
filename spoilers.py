import regex
import json
import os
import time
from post import slack_bot
import post

def get_new_spoilers():
	matches = regex.all_matches_from_page(new_spoiler_page(), '[a-zA-Z0-9_]*(?<!ogw|c15|bfz)/cards/[^.]*\.jpg')
	matches.reverse()
	return matches

def new_spoiler_page():
	return 'http://mythicspoiler.com/newspoilers.html'

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

def main(set, outchannel, logging):
	slack_bot = get_bot(outchannel=='slack')
	gone_bad = False
	post.write_to_log('Starting up...', logging=="log")
	try:
		data_directory = os.environ['OPENSHIFT_DATA_DIR']
	except:
		data_directory = 'data'
	while not gone_bad:
		try:
			spoiled = []
			new_spoilers = 0
			spoiled_file = '{!s}/{!s}.spoiled'.format(data_directory, set)
			try:
				with open(spoiled_file) as file:
					spoiled = json.loads(file.read())
			except:
				pass
			try:
				spoilers = spoiler_page_html(set)
			except:
				post.write_to_log('Couldn\'t connect to {!s}'.format(spoiler_page(set)), logging=="log")
			else:
				for spoiler in spoilers:
					if spoiler not in spoiled:
						image_url = '{!s}{!s}'.format(spoiler_page(set), spoiler)
						slack_bot.post_images([image_url], 'New {!s} spoiler'.format(set))
						spoiled.append(spoiler)
						new_spoilers += 1
				if new_spoilers == 0:
					post.write_to_log('No new spoilers right now', logging=="log")
				try: 
					with open(spoiled_file, 'w+') as file:
						file.write(json.dumps(spoiled))
				except:
					slack_bot.post_message('I have failed. Dying now.')
					gone_bad = True
		except:
			post.write_to_log('Failed to get spoilers', logging=="log")
		if not gone_bad:
			time.sleep(300)

def run_once(outchannel, logging):
	slack_bot = get_bot(outchannel=='slack')
	try:
		data_directory = os.environ['OPENSHIFT_DATA_DIR']
	except:
		data_directory = 'data'
	spoiled = []
	spoilers_to_post = []
	set = ''
	new_spoilers = 0
	spoiled_file = '{!s}/new.spoiled'.format(data_directory)
	try:
		with open(spoiled_file) as file:
			spoiled = json.loads(file.read())
	except:
		pass
	try:
		spoilers = get_new_spoilers()
	except:
		post.write_to_log('Couldn\'t connect to {!s}'.format(new_spoiler_page()), logging=="log")
	else:
		for spoiler in spoilers:
			if spoiler not in spoiled:
				image_url = 'http://mythicspoiler.com/{!s}'.format(spoiler)
				spoiled.append(spoiler)
				spoilers_to_post.append(image_url)
				set = spoiler.split('/')[0]
				new_spoilers += 1
				break
		if new_spoilers > 0:
			slack_bot.post_images(spoilers_to_post, 'New {!s} spoiler'.format(set.upper()))
		else:
			post.write_to_log('No new spoilers right now', logging=="log")
		try: 
			with open(spoiled_file, 'w+') as file:
				file.write(json.dumps(spoiled))
		except:
			slack_bot.post_message('I have failed. Dying now.')
			gone_bad = True

if __name__ == "__main__":
	#outchannel = 'console'
	outchannel = 'slack'
    #logging = 'console'
	logging = 'log'
	run_once(outchannel, logging)