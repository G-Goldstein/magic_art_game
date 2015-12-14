from websocket import create_connection

import requests
import json

def connect():
	sesh = requests.session()
	message = {'token': 'xoxp-15833257441-15833975863-15834190422-96eec85b0c'}
	response = sesh.post('https://slack.com/api/rtm.start', data = message).json()
	print(response['url'])
	ws = create_connection(response['url'])
	ws.sock.setblocking(0)
	print('Connected')

def main():
	connect()

if __name__ == '__main__':
	main()