"""
Basic connector class to PostgreSQL containers (Docker) via psycopg2.
Currently still on the Psycopg2 version that is before the big 2.8 changes (then psycopg2-binary package),
so there might be some changes introduced since the inception of this file.

Essentially bringing up all the necessary connection stuff, and reducing the interface to the necessary project
stuff. Building connection, pushing new data, and committing that.
"""

import psycopg2


class PostgresConnector:

    def __init__(self, database="postgres", user="postgres", password="postgres", host="127.0.0.1", port=5434):
        """
        Sets up database connection properties via psycopg2. Also wrapping this in a __enter__ / __exit__, so we do
        not lose any important information later.
        :param database: (str) database name.
        :param user: (str) User name to get access to the Postgres database.
        :param password: (str) Corresponding user password.
        :param host: (IP) IP address (in string format) for the host of the postgres database.
        :param port: (integer) Port at which to access the database.
        """
        self.database = database
        self.user = user
        self.password = password
        self.host = host
        self.port = port

    def __enter__(self):
        """
        Establishes context and then returns self
        :return: self
        """
        self.connection = psycopg2.connect(database=self.database,
                                           user=self.user,
                                           password=self.password,
                                           host=self.host,
                                           port=self.port)

        self.cursor = self.connection.cursor("temporary_dummy")

        return self

    # Thinking about adding a separate .push() or .get() function, but that would simply be an abstraction layer
    # for functions already available in Psycopg2, which I don't see a reason for...

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Leaving the context will store the results and try to save every transaction before shutting down.
        :param exc_type: Exception type
        :param exc_val: Exception value
        :param exc_tb: Exception traceback
        :return: (None)
        """
        # persist
        self.connection.commit()
        # clean up
        try:
            self.cursor.close()
        except psycopg2.ProgrammingError:
            pass
        self.connection.close()
