import json
import post

live = False

message = 'NPH'
url = 'http://static.independent.co.uk/s3fs-public/thumbnails/image/2014/03/12/09/neil-patrick-harris.jpg'

def post_message(message):
	with open('magic_art_game.settings') as config:
		settings = json.loads(config.read())
		magic_bot = post.slack_bot(settings['magic_channel_url'], settings['magic_channel_name'], settings['magic_bot_name'], settings['magic_bot_icon'], live)
		magic_bot.post_message(message)

def post_image(url, message):
	with open('magic_art_game.settings') as config:
		settings = json.loads(config.read())
		magic_bot = post.slack_bot(settings['magic_channel_url'], settings['magic_channel_name'], settings['magic_bot_name'], settings['magic_bot_icon'], live)
		images = [url]
		magic_bot.post_images(images, message)

post_image(url, message)