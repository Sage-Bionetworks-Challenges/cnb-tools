"""General class representing a Synapse entity."""

import synapseclient
from synapseclient.core.exceptions import SynapseNoCredentialsError


class SynapseBase:
    def __init__(self, uid=None):
        self._syn = self._check_login()
        self._uid = uid

    @property
    def syn(self) -> str:
        """Synapse object with authentication."""
        return self._syn

    @syn.setter
    def syn(self, _: str) -> None:
        raise SynapseInternalError("syn object is read-only")

    @property
    def uid(self) -> str:
        """Synapse entity's unique ID."""
        return self._uid

    @uid.setter
    def uid(self, value: str) -> None:
        self._uid = value

    # pylint: disable=unsupported-binary-operation
    @staticmethod
    def _check_login() -> synapseclient.Synapse | None:
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
