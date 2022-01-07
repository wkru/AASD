from spade.agent import Agent


class BrokerDirectoryAgent(Agent):
    async def setup(self):
        print(f'{repr(self)} started')

    def __repr__(self):
        return str(self.__class__.__name__)
