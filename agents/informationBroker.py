from spade.agent import Agent
from spade.behaviour import OneShotBehaviour
from spade.template import Template

from messages import requestManagement


class InformationBrokerAgent(Agent):
    class RecvBehav(OneShotBehaviour):
        async def run(self):
            print("RecvBehav running")
            self.requests = [{'id': 1, 'category': 'salt', 'comment': 'Himalaya salt', 'username': 'user1@localhost'}]
            msg = await self.receive(timeout=1000)  # wait for a message for 10 seconds
            if msg:
                if msg.metadata['performative'] == 'request':
                    resp = requestManagement.Response(to=str(msg.sender), data=self.requests)
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
