import urllib.request

def main():
	request_url = 'http://jhc-magicartgame.rhcloud.com/'
	page = urllib.request.urlopen(request_url)
	print('Completed successfully')

if __name__ == '__main__':
	main()