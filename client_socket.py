import socket
import pickle
import argparse
import threading
import select
import queue
import sys
"""
parser = argparse.ArgumentParser(description='Connect to server')
parser.add_argument('--host', default='127.0.0.1')
parser.add_argument('-p', '--port', default=8080)
args = parser.parse_args()
print(args.host)
print(args.port)
"""

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = socket.gethostname()
port = 8080
s.connect((host, port))
q = queue.Queue()

def send_obj(s, obj):
    b = pickle.dumps(obj)
    s.sendall('{:04d}'.format(len(b)).encode())
    s.sendall(b)

def recv_obj(s):
    length_b = recv_length(s, 4)
    length = int(length_b.decode())
    data = recv_length(s, length)
    obj = pickle.loads(data)
    if obj == "username_dup":
        sys.exit("Username alredy exist. Please choose another one.")
    return obj

def recv_length(s, length):
    data = b''
    while len(data) < length:
        msg = s.recv(length - len(data))
        if msg == b'':
            raise Exception('Connection closed')
        data += msg
    return data

nickname = input("Enter your nickname: ")
nickname_save = {"user": nickname}
send_obj(s, nickname_save)
print(recv_obj(s))

def sender():
     while True:
         message = input("->")
         q.put({'message': message, 'user': nickname})

def receiver():
    while True:
        # pokud je ve fronte neco, co mame poslat, posleme to
        while not q.empty():
            send_obj(s, q.get())
        # pokud server neco poslal, vypiseme to
        rlist, _, _ = select.select([s], [], [], 0.1)
        if s in rlist:
            print(recv_obj(s))

t_sender = threading.Thread(target=sender)
t_sender.start()
t_receiver = threading.Thread(target=receiver)
t_receiver.start()

