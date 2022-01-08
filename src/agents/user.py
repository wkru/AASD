import json

from spade.agent import Agent
from spade.behaviour import OneShotBehaviour, CyclicBehaviour
from spade.template import Template

from messages import requestManagement, productVaultServices

import time

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

            msg = requestManagement.Retrieve(to='information-broker-1@localhost')

            await self.send(msg)
            print("Message sent!")

    class VaultOffersReqBehav(OneShotBehaviour):
        async def run(self):
            print('VaultOffersReqBehav running')

            msg = productVaultServices.OffersRetrieve(to=self.agent.product_vault_jid)
            await self.send(msg)
            print("Message sent!")

    class VaultOffersRespBehav(CyclicBehaviour):
        async def run(self):
            print("VaultOffersRespBehav running")
            msg = await self.receive(timeout=1000)
            if msg:
                print("Message received with content: {}".format(msg.body))
            else:
                pass

    class VaultCategoriesReqBehav(OneShotBehaviour):
        async def run(self):
            print('VaultCategoriesReqBehav running')

            msg = productVaultServices.CategoriesRetrieve(to=self.agent.product_vault_jid)
            await self.send(msg)
            print("Message sent!")

    class VaultCategoriesRespBehav(CyclicBehaviour):
        async def run(self):
            print("VaultCategoriesRespBehav running")
            msg = await self.receive(timeout=1000)
            if msg:
                print("Message received with content: {}".format(msg.body))
            else:
                pass

    class VaultAddBehav(OneShotBehaviour):
        async def run(self):
            print('VaultAddBehav running')

            msg = productVaultServices.AddProductRequest(to=self.agent.product_vault_jid,
                                                         data=self.agent.get('vault_add_product_data'))
            await self.send(msg)
            print("Message sent!")

    class VaultGetReqBehav(OneShotBehaviour):
        async def run(self):
            print('VaultGetReqBehav running')

            msg = productVaultServices.GetProductRequest(to=self.agent.product_vault_jid,
                                                         data=self.agent.get('vault_get_product_data'))
            await self.send(msg)
            print("Message sent!")

    class VaultGetRespBehav(CyclicBehaviour):
        async def run(self):
            print("VaultGetRespBehav running")
            msg = await self.receive(timeout=1000)
            if msg:
                print("Message received with content: {}".format(msg.body))
            else:
                pass

    async def setup(self):
        print("SenderAgent started")

        self.product_vault_jid = 'product-vault-1@localhost'

        b = self.AskForRequestsBehav()
        self.add_behaviour(b)
        c = self.RecvBehav()
        self.add_behaviour(c)

        vault_offers_resp_b = self.VaultOffersRespBehav()
        vault_offers_resp_template = Template()
        vault_offers_resp_template.sender = self.product_vault_jid
        vault_offers_resp_template.set_metadata("performative", "response")
        vault_offers_resp_template.set_metadata("protocol", "vault_offers")
        self.add_behaviour(vault_offers_resp_b, vault_offers_resp_template)

        vault_categories_resp_b = self.VaultCategoriesRespBehav()
        vault_categories_resp_template = Template()
        vault_categories_resp_template.sender = self.product_vault_jid
        vault_categories_resp_template.set_metadata("performative", "response")
        vault_categories_resp_template.set_metadata("protocol", "vault_categories")
        self.add_behaviour(vault_categories_resp_b, vault_categories_resp_template)

        vault_get_resp_b = self.VaultGetRespBehav()
        vault_get_resp_template = Template()
        vault_get_resp_template.sender = self.product_vault_jid
        vault_get_resp_template.set_metadata("performative", "response")
        vault_get_resp_template.set_metadata("protocol", "vault_get")
        self.add_behaviour(vault_get_resp_b, vault_get_resp_template)

