import json

from spade.agent import Agent
from spade.behaviour import OneShotBehaviour
from spade.message import Message


class UserAgent(Agent):
    class RecvBehav(OneShotBehaviour):
        async def run(self):
            print("RecvBehav (UserAgent) running")

            msg = await self.receive(timeout=1000)
            if msg:
                msg_json = json.loads(msg.body)
                if msg_json['data_type'] == 'requests':
                    for product in msg_json['requests']:
                        print('ID:', product['id'])
                        print('Category:', product['category'])
                        print('Comment:', product['comment'])
                print("Message received with content: {}".format(msg.body))
            else:
                print("Did not receive any message after 1000 seconds")

            # stop agent from behaviour
            await self.agent.stop()

    class AskForRequestsBehav(OneShotBehaviour):
        async def run(self):
            print("AskForRequestsBehav running")
            msg = Message(to="request-registry@localhost")     # Instantiate the message
            msg.set_metadata("performative", "request")  # Set the "inform" FIPA performative
            msg.body = json.dumps({'data_type': 'requests'}) # Set the message content

            await self.send(msg)
            print("Message sent!")

    async def setup(self):
        print("SenderAgent started")
        b = self.AskForRequestsBehav()
        self.add_behaviour(b)
        c = self.RecvBehav()
        self.add_behaviour(c)
