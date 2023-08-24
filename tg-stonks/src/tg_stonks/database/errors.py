from typing import final


class DbError(Exception):
    """
    Database exception. Should only be raised when unspecified && unexpected error
    happened while working with the database.

    Also, all other exceptions related to the operation
    of any database should inherit from this exception.
    """
    pass


@final
class DbUserNotFound(DbError):
    """
    Should be raised when the user was not found in the table storing users
    of the database schema.
    """
    pass


@final
class DbInstrumentNotFound(DbError):
    """
    Should be raised when instrument was not found in the table storing
    financial instruments of the database schema.
    """
    pass


@final
class DbUserSettingsInvalid(DbError):
    """
    Should be raised when user settings violate the JSON settings schema,
    when they are created or validated.
    """
    pass
