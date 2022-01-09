import json
import logging

from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.template import Template

from messages import productVaultServices


class ProductVaultAgent(Agent):
    async def setup(self):

        self.set('offers', {0: {'category': 'Salt', 'comment': 'A bag of salt', 'location': 'Szatnia WEiTI'}})
        self.set('categories', ['Salt', 'Pepper', 'Sugar'])
        self.set('next_offer_id', len(self.get('offers')))

        offers_b = self.OffersBehav()
        offers_req_template = Template()
        offers_req_template.set_metadata("performative", "request")
        offers_req_template.set_metadata("protocol", "vault_offers")
        self.add_behaviour(offers_b, offers_req_template)

        categories_b = self.CategoriesBehav()
        categories_req_template = Template()
        categories_req_template.set_metadata("performative", "request")
        categories_req_template.set_metadata("protocol", "vault_categories")
        self.add_behaviour(categories_b, categories_req_template)

        add_b = self.AddBehav()
        add_req_template = Template()
        add_req_template.set_metadata("performative", "request")
        add_req_template.set_metadata("protocol", "vault_add")
        self.add_behaviour(add_b, add_req_template)

        get_b = self.GetBehav()
        get_req_template = Template()
        get_req_template.set_metadata("performative", "request")
        get_req_template.set_metadata("protocol", "vault_get")
        self.add_behaviour(get_b, get_req_template)


    class OffersBehav(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=1000)
            if msg:
                resp = productVaultServices.OffersResponse(to=str(msg.sender), data=self.agent.get('offers'))
                await self.send(resp)


    class CategoriesBehav(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=1000)
            if msg:
                resp = productVaultServices.CategoriesResponse(to=str(msg.sender), data=self.agent.get('categories'))
                await self.send(resp)

    class AddBehav(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=1000)
            if msg:
                try:
                    msg_contents = json.loads(msg.body)
                    assert {'category', 'comment', 'location'} == set(msg_contents.keys())
                    assert msg_contents['category'] >= 0
                    assert msg_contents['category'] < len(self.agent.get('categories'))
                    self.agent.get('offers')[self.agent.get('next_offer_id')] = msg_contents
                    self.agent.set('next_offer_id', self.agent.get('next_offer_id') + 1)
                except:
                    logging.info('Malformed AddToProductVault message received')


    class GetBehav(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=1000)
            if msg:
                try:
                    msg_contents = json.loads(msg.body)
                    assert {'id'} == set(msg_contents.keys())
                    received_id = int(msg_contents['id'])
                    assert received_id in self.agent.get('offers').keys()
                    offers = self.agent.get('offers')
                    offer = offers.pop(received_id)
                    self.agent.set('offers', offers)
                    resp = productVaultServices.GetProductResponse(to=str(msg.sender),
                                                                   data=offer)

                    await self.send(resp)
                except:
                    logging.info('Malformed GetFromProductVault message received')
