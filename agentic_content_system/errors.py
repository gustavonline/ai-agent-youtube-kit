"""Small, user-facing exception types for the CLI."""


class ACSUserError(Exception):
    """An expected input, contract, or runtime failure."""


class ACSCommandError(ACSUserError):
    """A controlled external command failed."""
