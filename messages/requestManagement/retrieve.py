from spade.message import Message

ontology = 'sharing'


class Retrieve(Message):
    def __init__(self, to):
        super().__init__(to=to, metadata={'performative': 'request', 'ontology': ontology})
