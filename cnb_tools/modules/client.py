"""Base module for cnb-tools, including Synapse client management and custom exceptions."""

import synapseclient
from synapseclient.core.exceptions import SynapseNoCredentialsError


def get_synapse_client() -> synapseclient.Synapse:
    """Return an authenticated Synapse client.

    Authenticates using credentials from ``~/.synapseConfig`` or the
    ``SYNAPSE_AUTH_TOKEN`` environment variable.

    Raises:
        SynapseLoginError: If no credentials are available.
    """
    try:
        return synapseclient.login(silent=True)
    except SynapseNoCredentialsError as err:
        raise SynapseLoginError(
            f"⛔ {err}\n\n"
            "Steps on how to provide your Synapse credentials to "
            "cnb-tools are available here: "
            "https://sage-bionetworks-challenges.github.io/cnb-tools/#requirements"
        ) from err


class SynapseLoginError(SystemExit):
    pass


class UnknownSynapseID(SystemExit):
    pass
