# encoding=utf-8
import socket
import re
import os

USER_ID = 987654321 # your own userid

bfiles = []
files = ['a.cpp', 'b.cpp', 'c.cpp', 'd.cpp', 'e.cpp']
opt = {'directory': False, 'X': False, 'maxmatches': 1e7, 'show': 250,
       'language': 'cc', 'comment': ''}

def readline(sock):
  buffer = b''
  while not buffer or buffer[-1] != '\n':
    b = sock.recv(1)
    if b < 0:
      raise Exception(b)
    buffer += b
  return buffer.decode('utf-8')

def sendfile(sock, id, filename, lang='cc'):
  print('Sending {0}'.format(filename))
  file_id = re.sub('\s', '_', filename)
  file_size = os.path.getsize(filename)
  sock.sendall('file {0} {1} {2} {3}\n'.format(
    str(id), lang, str(file_size), file_id).encode('utf-8'))
  with open(filename, 'rb') as f:
    read = 0
    while read < file_size:
      buffer = f.read(1024)
      sock.sendall(buffer)
      read += len(buffer)
  print('Done')

print('Connecting')
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('moss.stanford.edu', 7690))
print('Connected, sending request')
sock.sendall('moss {0}\n'.format(USER_ID).encode('utf-8'))
sock.sendall('directory {0}\n'.format(int(opt['directory'])).encode('utf-8'))
sock.sendall('X {0}\n'.format(int(opt['X'])).encode('utf-8'))
sock.sendall('maxmatches {0}\n'.format(int(opt['maxmatches'])).encode('utf-8'))
sock.sendall('show {0}\n'.format(int(opt['show'])).encode('utf-8'))
sock.sendall('language {0}\n'.format(opt['language']).encode('utf-8'))
print('Request sent, waiting for response')
succ = readline(sock).strip()
print(succ)
if succ == 'no':
  sock.sendall('end\n')
  print('Unrecognized language')
  exit(1)

for bfile in bfiles:
  sendfile(sock, 0, bfile, opt['language'])

for i, file in enumerate(files):
  sendfile(sock, i + 1, file, opt['language'])

print('All files sent, sending query')

sock.sendall('query 0 {0}\n'.format(opt['comment']).encode('utf-8'))
print('Query sent, waiting for server')
print(readline(sock))
