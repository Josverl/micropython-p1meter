# Mock for umqtt.simple — used by tests running on the MicroPython Unix port.


class MQTTException(Exception):
    pass


class MQTTClient:
    def __init__(self, client_id, server, port=0, user=None, password=None,
                 keepalive=0, ssl=False, ssl_params={}):
        self.client_id = client_id
        self.server = server
        self.port = port
        self.sock = None

    def connect(self, clean_session=True):
        pass

    def disconnect(self):
        pass

    def publish(self, topic, msg, retain=False, qos=0):
        pass

    def subscribe(self, topic, qos=0):
        pass

    def ping(self):
        pass

    def set_callback(self, f):
        pass

    def check_msg(self):
        pass

    def wait_msg(self):
        pass
