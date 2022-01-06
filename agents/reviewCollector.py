import json

from spade.agent import Agent
from spade.behaviour import OneShotBehaviour
from spade.message import Message


class ReviewCollectorAgent(Agent):
    async def setup(self):
        print(f'{repr(self)} started')

    def __repr__(self):
        return str(self.__class__.__name__)
