import socket
import pickle
import threading
import queue
import select

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = socket.gethostname()
port = 8080
s.bind((host, port))
s.listen(5)
nickname_list = []


def send_obj(s, obj):
    b = pickle.dumps(obj)
    s.sendall('{:04d}'.format(len(b)).encode())
    s.sendall(b)


def recv_obj(s):
    length_b = recv_length(s, 4)
    length = int(length_b.decode())
    data = recv_length(s, length)
    obj = pickle.loads(data)
    return obj


def recv_length(s, length):
    data = b''
    while len(data) < length:
        msg = s.recv(length - len(data))
        if msg == b'':
            raise Exception('Connection closed')
        data += msg
    return data


def listener(conn, addr):
    q = queue.Queue()
    print("Accepted connection from " + str(addr))
    client_queues.add(q)

    try:
        nickname = recv_obj(conn)
        if nickname['user'] not in nickname_list:
            nickname_list.append(nickname['user'])
            print(("User " + "[" + nickname['user'] + "]" + " is connected\n"))
            for c in client_queues:
                c.put(("User " + "[" + nickname['user'] + "]" + " is connected\n"))
        else:
            w_nickname = ("username_dup")
            send_obj(conn, w_nickname)
            # conn.shutdown( "User name is alredy exist. Please choose another one.")
            conn.close()

        while True:
            while not q.empty():
                msg = q.get()
                send_obj(conn, msg)
            rlist, _, _ = select.select([conn], [], [], 0.1)
            if conn in rlist:
                msg = recv_obj(conn)
                print(("[" + msg['user'] + "]" + ": " + msg['message'] + "\n"))
                for c in client_queues:
                    c.put(("[" + msg['user'] + "]" + ": " + msg['message'] + "\n"))

    finally:

        client_queues.remove(q)
        conn.close()


client_queues = set()
threads = []

while True:
    print("Server is listenning...")
    conn, addr = s.accept()
    t = threading.Thread(target=listener, args=(conn, addr))
    threads.append(t)
    t.start()

s.close()
nickname_list.clear()