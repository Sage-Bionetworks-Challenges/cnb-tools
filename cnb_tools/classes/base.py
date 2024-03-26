"""General class representing a Synapse entity."""

import sys
import synapseclient
from synapseclient.core.exceptions import SynapseNoCredentialsError


class SynapseBase:
    def __init__(self):
        self.syn = self._check_login()

    @staticmethod
    def _check_login() -> synapseclient.Synapse | None:
        try:
            return synapseclient.login(silent=True)
        except SynapseNoCredentialsError as err:
            print(err)
            sys.exit()
