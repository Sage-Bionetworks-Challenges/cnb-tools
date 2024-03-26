"""Class representing a challenge team or individual participant."""

from synapseclient.core.exceptions import SynapseHTTPError

from cnb_tools.classes.base import BaseSynapseEntity


class Submitter(BaseSynapseEntity):
    def __init__(self, uid):
        super().__init__()
        self.uid = uid

    def pretty_print(self):
        try:
            return self.syn.getTeam(self.uid).get("name")
        except SynapseHTTPError:
            return self.syn.getUserProfile(self.uid).get("userName")
