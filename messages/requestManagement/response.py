import json

from spade.message import Message

ontology = 'sharing'


class Response(Message):
    def __init__(self, to, data):
        body = json.dumps(data)
        super().__init__(to=to, body=body, metadata={'performative': 'inform', 'ontology': ontology})
