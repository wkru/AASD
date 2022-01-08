from utils import Location

import json

from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.template import Template

from config import SERVICES

from messages import serviceDiscovery

class BrokerDirectoryAgent(Agent):
    async def setup(self):
        print(f'{repr(self)} started')

        service_request = self.ServiceRequest()
        template = Template()
        template.set_metadata("performative", "request")
        template.set_metadata("protocol", "local_services")
        self.add_behaviour(service_request, template)

    def __repr__(self):
        return str(self.__class__.__name__)

    class ServiceRequest(CyclicBehaviour):
        async def run(self):
            print("ServiceRequest running")
            msg = await self.receive(timeout=1000)  # wait for a message for 10 seconds
            if msg:
                try:
                    msg_content = json.loads(msg.body)

                    user_location = Location(msg_content[0], msg_content[1])

                    lengths = [loc[0].distance_to(user_location) for loc in SERVICES]
                    index_min = min(range(len(lengths)), key=lengths.__getitem__)

                    resp = serviceDiscovery.ServicesRespond(to=str(msg.sender), data=SERVICES[index_min][1])
                    await self.send(resp)
                except:
                    print('Malformed ServicesRequest message received')
                print("Message received with content: {}".format(msg.body))
            else:
                print("Did not receive any message after 10 seconds")