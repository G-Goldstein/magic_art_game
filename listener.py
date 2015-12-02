import socket
import sys
import os
from post import write_to_log

def main():
	try:
		HOST = os.environ['OPENSHIFT_PYTHON_IP']
		PORT = int(os.environ['OPENSHIFT_PYTHON_PORT'])
		write_to_log('Attempting to listen on: {!s}:{!s}'.format(HOST, PORT))
	except:
		HOST = ''
		PORT = 8080

	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	write_to_log('Socket created')

	try:
		s.bind((HOST, PORT))
	except socket.error as msg:
		write_to_log('Bind failed. Error: {!s}'.format(msg))
		sys.exit()

	write_to_log('Socket bind complete')

	s.listen(10)
	write_to_log('Socket now listening')

	while 1:
		conn, addr = s.accept()
		write_to_log('Connected with {!s}:{!s}'.format(addr[0], addr[1]))

	s.close()

if __name__ == '__main__':
	main()