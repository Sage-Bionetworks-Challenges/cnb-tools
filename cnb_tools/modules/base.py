"""Base module for cnb-tools, including Synapse client management and custom exceptions."""

import synapseclient
from synapseclient.core.exceptions import SynapseNoCredentialsError


def get_synapse_client():
    try:
        return synapseclient.login(silent=True)
    except SynapseNoCredentialsError as err:
        raise SynapseLoginError(
            f"⛔ {err}\n\n"
            "Steps on how to provide your Synapse credentials to "
            "cnb-tools are available here: "
            "https://sage-bionetworks-challenges.github.io/cnb-tools/#requirements"
        ) from err


class SynapseInternalError(Exception):
    pass


class SynapseLoginError(SystemExit):
    pass


class UnknownSynapseID(SystemExit):
    pass
