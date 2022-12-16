import socket
import selectors
import types
from constants import POLL, SUBSCRIBE, HOST, PORT
from mqtt_connector import MQTTConnector


class ServerConnector:
    def __init__(self, host, port):
        self.mqtt = MQTTConnector()
        self.host = host
        self.port = port
        self.lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.lsock.bind((self.host, self.port))
        self.lsock.listen()
        self.sel = selectors.DefaultSelector()
        self.lsock.setblocking(False)
        self.subscribers = []

    def init(self):
        self.mqtt.run()

    def read(self, key, mask):
        sock = key.fileobj
        data = key.data
        self.check_for_messages(data)
        self.handle_read_actions(data, mask, sock)
        self.send_message(data, mask, sock)

    def send_message(self, data, mask, sock):
        if mask & selectors.EVENT_WRITE:
            if data.outb:
                print(f"Echoing {data.outb!r} to {data.addr}")
                sent = sock.send(data.outb)
                data.outb = data.outb[sent:]

    def handle_read_actions(self, data, mask, sock):
        if mask & selectors.EVENT_READ:
            recv_data = sock.recv(1024)
            if recv_data:
                command = recv_data.decode().split()
                if len(command) == 0:
                    return
                user_command = command[0]
                session_id = data.addr[1]
                if session_id in self.subscribers:
                    return
                if user_command == POLL:
                    self.subscribers.append(session_id)
                elif user_command == SUBSCRIBE:
                    topic_name = command[1]
                    self.subscribe(session_id, topic_name)

    def subscribe(self, session_id, topic_name):
        self.mqtt.create_message_map(session_id)
        self.mqtt.create_subscriber_session_map(topic_name, session_id)
        self.mqtt.subscribe(topic_name, session_id)

    def check_for_messages(self, data):
        messages = self.mqtt.get_messages()
        if messages:
            for id, message in messages.items():
                if len(message) > 0:
                    if id == data.addr[1] and id in self.subscribers:
                        m = message.pop() + '\n'
                        data.outb += m.encode()

    def accept(self, sock):
        conn, addr = sock.accept()
        print(f'accepted connection from {addr}')
        conn.setblocking(False)
        data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        self.sel.register(conn, events, data=data)

    def run(self):
        print("starting...")
        self.mqtt.run()
        self.sel.register(self.lsock, selectors.EVENT_READ, data=None)
        try:
            while True:
                events = self.sel.select(timeout=None)
                for key, mask in events:
                    if key.data is None:
                        self.accept(key.fileobj)
                    else:
                        self.read(key, mask)
        except KeyboardInterrupt:
            print("Caught keyboard interrupt, exiting")
        finally:
            self.sel.close()


if __name__ == '__main__':
    s_c = ServerConnector(host=HOST, port=PORT)
    s_c.run()

