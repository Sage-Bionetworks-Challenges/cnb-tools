"""Base module for cnb-tools.

Provides a shared Synapse client factory and custom exceptions used
throughout the package.
"""

import synapseclient
from synapseclient.core.exceptions import SynapseNoCredentialsError


def get_synapse_client() -> synapseclient.Synapse:
    """Return an authenticated Synapse client.

    Tip: Credentials
      Reads credentials from ``~/.synapseConfig`` or the
      ``SYNAPSE_AUTH_TOKEN`` environment variable. Run ``synapse config``
      to set up your credentials.

    Returns:
      An authenticated ``synapseclient.Synapse`` instance.

    Raises:
      SynapseLoginError: If no credentials are found.
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
