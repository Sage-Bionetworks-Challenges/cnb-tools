"""Class representing a challenge submission evaluation queue."""

from cnb_tools.classes.base import SynapseBase


class Queue(SynapseBase):
    def __init__(self, uid):
        super().__init__()
        self.uid = uid
        self.queue = self.syn.getEvaluation(uid)

    def __str__(self) -> str:
        return self.queue.name

    def get_challenge_name(self) -> str:
        parent_id = self.queue.contentSource
        return self.syn.get(parent_id).name
