from src.factories.abstractFactory import AbstractFactory
from src.agents.reviewCollector import ReviewCollectorAgent


class ReviewCollectorFactory(AbstractFactory):
    jid_template = 'review-collector'

    def create_agent(self) -> ReviewCollectorAgent:
        new_agent = self._create_agent(ReviewCollectorAgent)
        return new_agent
