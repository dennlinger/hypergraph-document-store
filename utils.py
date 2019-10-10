"""
Contains functions that are shared between multiple scripts, like the logger handling or small helper functions.
"""

import logging
import itertools as itt

from psycopg2 import ProgrammingError, IntegrityError
from psycopg2.extras import execute_values


def take(iterable, n):
    """
    Returns the first n values of an iterable object.
    :param iterable: An object (list, dict,...) containing several elements.
    :param n: (int) Number of elements to be returned.
    :return: First n elements of the iterable object.
    """
    return list(itt.islice(iterable, n))


def set_up_logger(name, file_path, level=logging.INFO, verbose=True):
    """
    Creates basic logger object that optionally also logs to command-line.
    :param name: (string) Name of the logger. Should be called with __name__.
    :param file_path: (string) File location of the output handler.
    :param level: (logging.LEVEL) Specifies the logging level which is output.
    :param verbose: (boolean) If set to True, will also log with the appropriate level to stdout.
    :return: logging.Logger object with the specified properties.
    """

    # create base logger
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # format the date accordingly
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s \t: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

    # add handler for write to file
    fh = logging.FileHandler(file_path)
    fh.setLevel(level)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    # add handler for stream output if wanted
    if verbose:
        sh = logging.StreamHandler()
        sh.setLevel(level)
        sh.setFormatter(formatter)
        logger.addHandler(sh)

    return logger


def check_table_existence(logger, connector, table_name):
    logger.info("Checking whether {} table already exists...".format(table_name))
    # see https://stackoverflow.com/questions/1874113/
    # checking-if-a-postgresql-table-exists-under-python-and-probably-psycopg2
    # for a different approach.
    # try:
    #     connector.cursor.execute("SELECT COUNT(*) FROM {}".format(table_name))
    # except ProgrammingError as err:
    #     logger.error("{} table does not exist!\n {}".format(table_name, err))
    #     return 0
    #
    # return 1
    connector.cursor.execute("SELECT EXISTS(SELECT * FROM information_schema.tables "
                             "WHERE table_name = %s);", (table_name, ))

    return connector.cursor.fetchone()[0]


def insert_into_table(open_pc, table_name, table_structure, values, logger):
    try:
        execute_values(open_pc.cursor,
                       "INSERT INTO {} ({}) VALUES %s".format(table_name, table_structure), values)

    except IntegrityError as err:
        logger.error("Values with previously inserted primary key detected!\n {}".format(err))
        return 0

    return 1