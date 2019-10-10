"""
Create one big file that can (re)create an entire dataset structure.
"""

from DocumentGenerator import DocumentGenerator
from TermGenerator import TermGenerator
from HyperedgeGenerator import HyperedgeGenerator
from GenerateNewSchema import SchemaCreator

from subprocess import run
import argparse
import time


def str2bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


def get_parser():
    """
    Creates an argument parser with the relevant options.
    :return: (argparser) Argument handle.
    """
    args = argparse.ArgumentParser(description="Process all tables.")

    args.add_argument("-n", "--number-of-documents", type=int, default=5000,
                      help="Number of documents that will be processed.")
    args.add_argument("-r", "--restart", type=str2bool, nargs="?", const=True, default=True,
                      help="Restarting docker before processing. Saves time deleting values.")
    args.add_argument("-p", "--port", type=int, default=5435,
                      help="Port for a new docker container.")
    args.add_argument("-d", "--duplicate", type=str2bool, nargs="?", const=True, default=False,
                      help="Whether to start a new docker instance. Not in conjunction with --restart!")
    args.add_argument("--name", type=str, default="RSS-news-test",
                      help="Name of the docker container. Must be distinct from the default for -d!")
    args.add_argument("-i", "--image", type=str, default="dennlinger/hyppograph:final",
                      help="Name of the docker image to be used.")
    args.add_argument("-v", "--volume", type=str2bool, nargs="?", const=True, default=True,
                      help="Whether the attached data should be stored in a volume or not.")
    args.add_argument("-s", "--shm", type=str, default="256M")

    return args


def set_up(opts):
    if opts.restart:
        run(["docker", "rm", "-f", "RSS-news-test"])
        if opts.volume:
            run(["docker", "volume", "rm", "postgres-data"])
            run(["docker", "volume", "create", "postgres-data"])
            run(["docker", "run", "-d", "--mount", "source=postgres-data,destination=/var/lib/postgresql/data",
                 "-p", str(opts.port) + ":5432", "--name", opts.name, opts.image])
        else:
            run(["docker", "run", "-d", "--shm-size", opts.shm, "-p", str(opts.port)+":5432", "--name", opts.name, opts.image])

    if opts.duplicate:
        if opts.volume:
            raise ValueError("Can't duplicate and mount the same volume!")
        run(["docker", "run", "-d", "-p", str(opts.port) + ":5432", "--name", opts.name, opts.image])
        print("Finished setting up Docker instance.")


if __name__ == "__main__":

    # set up parser
    parser = get_parser()
    opts = parser.parse_args()

    # create new docker instance, if needed.
    set_up(opts)

    # manual interrupt to let docker start properly
    time.sleep(5)

    # Create all generators
    print("Starting with generation of all relevant documents...")
    dg = DocumentGenerator(port=opts.port, num_distinct_documents=opts.number_of_documents)
    tg = TermGenerator(num_distinct_documents=opts.number_of_documents, port=opts.port)
    hg = HyperedgeGenerator(port=opts.port)

    # Clear all tables.
    print("Clearing tables for re-insertion...")
    hg.clear_all_tables()

    tg.clear_table(tg.term_occurrence_table_name)
    tg.clear_table(tg.entity_table_name)
    tg.clear_table(tg.term_table_name)
    tg.clear_table(tg.sentence_table_name)

    dg.clear()

    # insert from scratch.
    dg.retrieve()
    dg.push()
    dg.remove_spike()

    # re-initialize due to the fact that previously the documents haven't been inserted!
    print("Pushing new documents...")
    tg = TermGenerator(num_distinct_documents=opts.number_of_documents, port=opts.port)
    tg.parse()
    tg.push_sentences()
    tg.push_terms()
    tg.push_entities()
    tg.push_term_occurrences()

    hg.create_edges_naively()

    # additionally serve an entity-only table.
    sc = SchemaCreator(port=opts.port)
    sc.create()
