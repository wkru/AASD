import json

from spade.agent import Agent
from spade.behaviour import OneShotBehaviour
from spade.message import Message
from spade.template import Template


class InformationBrokerAgent(Agent):
    class RecvBehav(OneShotBehaviour):
        async def run(self):
            print("RecvBehav running")
            self.requests = [{'id': 1, 'category': 'salt', 'comment': 'Himalaya salt', 'username': 'user3@localhost'}]
            msg = await self.receive(timeout=1000) # wait for a message for 10 seconds
            if msg:
                if json.loads(msg.body)['data_type'] == 'requests':
                    resp = Message(to=str(msg.sender))  # Instantiate the message
                    resp.set_metadata("performative", "inform")  # Set the "inform" FIPA performative
                    requests_to_send = {'requests': self.requests}
                    requests_to_send['data_type'] = 'requests'
                    resp.body = json.dumps(requests_to_send)  # Set the message content
                    await self.send(resp)
                print("Message received with content: {}".format(msg.body))
            else:
                print("Did not receive any message after 10 seconds")

            # stop agent from behaviour
            await self.agent.stop()

    async def setup(self):
        print("ReceiverAgent started")
        b = self.RecvBehav()
        template = Template()
        template.set_metadata("performative", "request")
        self.add_behaviour(b, template)
