import itertools

from paho.mqtt import client as mqtt_client
from paho.mqtt.client import topic_matches_sub

from constants import BROKER, MQQT_PORT


class MQTTConnector:
    def __init__(self):
        self.broker = BROKER
        self.port = MQQT_PORT
        self.received_message = []
        self.client = self.connect_mqtt()
        self.messages = {}
        self.subscriptions = {}

    def connect_mqtt(self):
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print("Connected to MQTT Broker!")
            else:
                print("Failed to connect, return code %d\n", rc)
        client = mqtt_client.Client('mqtt_client')
        client.on_connect = on_connect
        client.connect(self.broker, self.port)
        return client

    def create_messages(self, message, topic):
        matched_sessions = itertools.chain(*[
            session for subscribe_topic, session in self.subscriptions.items()
            if topic_matches_sub(subscribe_topic, topic)
        ])
        for session in matched_sessions:
            self.messages[session].append(message)

    def subscribe(self, topic: str, session_id: int):
        def on_message(client, userdata, msg):
            message = f"{msg.topic}: {msg.payload.decode()}"
            self.create_messages(message, topic)

        self.client.subscribe(topic)
        self.client.on_message = on_message

    def run(self):
        print('Starting mqtt')
        self.client.loop_start()

    def get_messages(self):
        return self.messages

    def create_message_map(self, session_id):
        self.messages[session_id] = []

    def create_subscriber_session_map(self, param, param2):
        if param not in self.subscriptions:
            self.subscriptions[param] = {param2}
        else:
            self.subscriptions[param].add(param2)
