import http.server
import socketserver

class MagicHandler(http.server.BaseHTTPRequestHandler):
	def do_GET(self):
		print(self.request)

PORT = 8000

httpd = socketserver.TCPServer(("", PORT), MagicHandler)

print("serving at port {!s}".format(PORT))
httpd.serve_forever()