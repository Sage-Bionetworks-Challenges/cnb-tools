"""Class representing a submission team or individual participant."""

from synapseclient.core.exceptions import SynapseHTTPError

from cnb_tools.classes.base import SynapseBase


class Submitter(SynapseBase):
    def __str__(self):
        try:
            return self.syn.getTeam(self.uid).get("name")
        except SynapseHTTPError:
            return self.syn.getUserProfile(self.uid).get("userName")
