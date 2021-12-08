import time
from spade.agent import Agent
from spade.behaviour import OneShotBehaviour
from spade.message import Message
from spade.template import Template
import json


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

if __name__ == "__main__":
    rragent = InformationBrokerAgent("request-registry@localhost", "aasd")
    future = rragent.start()
    future.result() # wait for receiver agent to be prepared.
    useragent = UserAgent("user3@localhost", "aasd")
    useragent.start()

    while rragent.is_alive():
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            useragent.stop()
            rragent.stop()
            break
    print("Agents finished")