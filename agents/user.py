import json

from spade.agent import Agent
from spade.behaviour import OneShotBehaviour

from messages.requestManagement.retrieve import Retrieve


class UserAgent(Agent):
    class RecvBehav(OneShotBehaviour):
        async def run(self):
            print("RecvBehav (UserAgent) running")

            if (msg := await self.receive(timeout=1000)) is not None:
                if str(msg.sender) == 'information-broker-1@localhost':
                    if msg.metadata['performative'] == 'inform':
                        msg_json = json.loads(msg.body)
                        for product in msg_json:
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

            msg = Retrieve(to='information-broker-1@localhost')

            await self.send(msg)
            print("Message sent!")

    async def setup(self):
        print("SenderAgent started")
        b = self.AskForRequestsBehav()
        self.add_behaviour(b)
        c = self.RecvBehav()
        self.add_behaviour(c)
