import requests
import json

class slack_bot:

	def __init__(self, hook_url, channel_name, bot_name, bot_icon, live=False):
		self.hook_url = hook_url
		self.default_message = {
		'channel': channel_name,
		'username': bot_name,
		'icon_url': bot_icon
		}
		self.live = live
		self.session = requests.session()

	def post_message(self, message_text):
		message = self.default_message.copy()
		message['text'] = message_text
		payload = {'payload':json.dumps(message)}
		self._send_or_simulate(payload, 'simulating post of message: {!s}'.format(message_text))

	def post_image(self, image_url, pretext="", fallback="Couldn't display image"):
		message = self.default_message.copy()
		attachment = {
		'image_url': image_url,
		'pretext': pretext,
		'fallback': fallback
		}
		message['attachments'] = [attachment]
		payload = {'payload':json.dumps(message)}
		self._send_or_simulate(payload, 'simulating post of image: {!s}'.format(image_url))

	def _send_or_simulate(self, payload, simulate_text):
		if self.live:
			self.session.post(self.hook_url, data=payload)
		else:
			print(simulate_text)