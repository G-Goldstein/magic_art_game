import http.server
import socketserver
from art_game import magic_art_game

class MagicHandler(http.server.BaseHTTPRequestHandler):
	def do_GET(self):
		print(self.request)

PORT = 8000

httpd = socketserver.TCPServer(("", PORT), MagicHandler)
print("running build script")
print("serving at port {!s}".format(PORT))

game = magic_art_game('magic_art_game.settings', 'impossible', live=True)

game.start_the_game()

httpd.serve_forever()