import socket
import sys
import os
from post import write_to_log

HOST = os.environ['OPENSHIFT_PYTHON_IP']
PORT = os.environ['OPENSHIFT_PYTHON_PORT']

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
write_to_log('Socket created')

try:
	s.bind((HOST, PORT))
except socket.error as msg:
	write_to_log('Bind failed. Error code: {!s} Message {!s}'.format(msg[0], msg[1]))
	sys.exit()

write_to_log('Socket bind complete')

s.listen(10)
write_to_log('Socket now listening')

while 1:
	conn, addr = s.accept()
	write_to_log('Connected with {!s}:{!s}'.format(addr[0], addr[1]))

s.close()