import json
import logging

from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.template import Template

from src.messages import serviceDiscovery
from src.config import SERVICES
from src.misc.location import Location


class BrokerDirectoryAgent(Agent):
    async def setup(self):
        service_request = self.ServiceRequest()
        template = Template()
        template.set_metadata("performative", "request")
        template.set_metadata("protocol", "local_services")
        self.add_behaviour(service_request, template)

    def __repr__(self):
        return str(self.__class__.__name__)

    class ServiceRequest(CyclicBehaviour):
        async def run(self):
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
                    logging.info('Malformed ServicesRequest message received')
