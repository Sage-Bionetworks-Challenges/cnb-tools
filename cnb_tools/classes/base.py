"""General class representing a Synapse entity."""

import sys
import synapseclient
from synapseclient.core.exceptions import SynapseNoCredentialsError


class SynapseBase:
    def __init__(self):
        self.syn = self._check_login()

    # pylint: disable=unsupported-binary-operation
    @staticmethod
    def _check_login() -> synapseclient.Synapse | None:
        try:
            return synapseclient.login(silent=True)
        except SynapseNoCredentialsError as err:
            print(f"⛔ {err}\n")
            print(
                "Steps on how to provide your Synapse credentials to "
                "cnb-tools are available here: "
                "https://sage-bionetworks-challenges.github.io/cnb-tools/#requirements"
            )
            sys.exit(1)
