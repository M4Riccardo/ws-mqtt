import json


class MessageDescriptor:

    def __init__(self, timestamp, type, value):
        self.timestamp = timestamp
        self.type = type
        self.value = value

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__)


class WebSocketMessageDescriptor:

    def __init__(self, deviceId, type, value, protocol):
        self.deviceId = deviceId
        self.type = type
        self.value = value
        self.protocol = protocol

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__)
