"""
Unlike AnalyzeTermOccurrence, we focus on the generated hyperedges in this file.
This includes the basic research on the number of entities in each hyperedge, as well as the average distance,
or some other "basic graph measures".

Note that we already have some simplifications on here, so it might be well worth to look at the underlying data more.
"""

from PostgresConnector import PostgresConnector

import numpy as np
import matplotlib.pyplot as plt

# import igraph

from pprint import PrettyPrinter
from collections import Counter


pp = PrettyPrinter()


def call(pc, query):
    """
    Calls the database with a specific query. Simple wrapper that takes away the pain.
    :param pc: (PostgresConnector) PostgresConnector object to connect to database.
    :param query: (string) SQL formatted query to be executed.
    :return: (list of tuples) Result of the query.
    """

    with pc as open_pc:
        open_pc.cursor.execute(query)
        result = open_pc.cursor.fetchall()

    print("{} results retrieved".format(len(result)))
    return result


def print_count(text, table):
    """
    Prints the number of elements in a table.
    :param text: (str) Displayed name in string
    :param table: (str) Name of the table in Postgres
    :return: None
    """
    query = "SELECT COUNT(*) FROM {}".format(table)
    count = call(pc, query)[0][0]
    print("Number of {}: {}".format(text, count))
    return count


def print_std(array):
    """
    Displays the standard deviation of a given array.
    :param array: (numpy.array) 1-D array of values.
    :return: (None)
    """
    print("Associated standard deviation was {:.4f}.".format(np.sqrt(np.var(array))))


def process_frequencies(array, text, hold=False):
    """
    Since terms and entities are basically processed in the same fashion, we can get a function doing the same
    for the both of them.
    :param array: (list) Holds the return from the SQL query.
    :param text: (str) Description for some of the print statements.
    :param hold: (boolean) When True, will plot both distributions in one.
    :return: (None)
    """

    values_only = np.array([el[1] for el in array])
    freq_counter = Counter(values_only)

    # for hold, we simply want that it plots in the same graph. Otherwise do everything.
    if not hold:
        print("Most occurring {} was '{}' with {} occurrences.".format(text, array[0][0], array[0][1]))
        print("Average number of {} occurrences was {:.4f}.".format(text, np.mean(values_only)))
        print_std(values_only)
        print("Median number of {} occurrences was {}.".format(text, np.median(values_only)))
        print("75 percentile for number of {} occurrences was {:.4f}.".format(text, np.percentile(values_only, 75)))
        print("99 percentile for number of {} occurrences was {:.4f}.".format(text, np.percentile(values_only, 99)))

        # fit = igraph.statistics.power_law_fit(freq_counter.values())
        # print("Calculated power-law exponent is {:.6f}, with kmin of {}.".format(fit.alpha, fit.xmin))

        plt.figure()

    ax = plt.subplot(111)
    ax.set_xscale("log")
    ax.set_yscale("log")

    ax.set_xlabel("k")
    ax.set_ylabel("p(k)")
    dist_x = freq_counter.keys()
    if hold:
        dist_y = np.array(list(freq_counter.values())) / len(values_only)
    else:
        dist_y = np.array(list(freq_counter.values())) / len(values_only)

    plt.scatter(dist_x, dist_y, marker=".", label=text)

    ax.legend()


    # create a line fit.
    # x = list(range(np.min(values_only), np.max(values_only), 10))
    # y = np.array([el**-fit.alpha for el in x])
    #
    # plt.plot(x, y, 'r')

    if not hold:
        fig_name = "./plots/" + text + "_distribution.png"
    else:
        fig_name = "./plots/both_distribution.png"
    plt.savefig(fig_name)


def plot_frequencies(query_results, file_prefix, title, x_label, y_label, type="bar", marker='o', bottom_adjust=0.0,
                     average=False):
    """
    Basic wrapper around the matplotlib interface.
    :param query_results: (list of tuples) Return value from the Postgres query. Used as plotting baseline.
    :param file_prefix: (str) Name for the plot file that will be generated.
    :param title: (str) Plot title.
    :param x_label: (str) Labeling for x axis.
    :param y_label: (str) Labeling for y axis.
    :param type: (str) Determines what kind of plot will be employed. "bar", "plot", "scatter" are valid options.
    :param marker: (str) Which kind of marker for line plots.
    :param bottom_adjust: (float) Parameter to account for tilted xticks.
    :param average: (boolean) If activated, plots the average.
    :return: (None) Will store file to disk.
    """

    x = [el[0] for el in query_results]
    y = [el[1] for el in query_results]

    plt.figure()
    ax = plt.subplot(111)

    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.set_title(title)

    if type == "bar":
        plt.bar(x,y)
    elif type == "plot":
        plt.plot(x,y, marker=marker)
    elif type == "scatter":
        plt.scatter(x,y)

    if average:
        ax.axhline(np.mean(y), color='red')

    for tick in ax.get_xticklabels():
        tick.set_rotation(90)

    plt.subplots_adjust(bottom=bottom_adjust)
    fn = "./plots/" + file_prefix + "_Plot.png"
    plt.savefig(fn)


if __name__ == "__main__":

    pc = PostgresConnector(port=5435)

    # basic info.
    sentence_count = print_count("sentences", "sentences")
    document_count = print_count("documents", "documents")
    term_count = print_count("terms", "terms")
    entity_count = print_count("entities", "entities")
    term_occurrences = print_count("term occurrences", "term_occurrence")
    # entity occurrences are a little bit different.
    query = "SELECT COUNT(*) FROM term_occurrence, terms WHERE term_occurrence.term_id = terms.term_id AND " \
            "terms.is_entity = true"
    entity_occurrences = call(pc, query)[0][0]
    print("Number of entity occurrences: {}".format(entity_occurrences))

    # document-grouped sentences
    query = "SELECT document_id, COUNT(document_id) FROM sentences " \
            "GROUP BY document_id ORDER BY COUNT(document_id) DESC"
    grouped_sentences = call(pc, query)
    lengths = np.array([el[1] for el in grouped_sentences])
    print("Longest document by number of sentences was doc_id {}, with {} sentences.".format(grouped_sentences[0][0],
                                                                                             grouped_sentences[0][1]))

    print("Average document length by number of sentences was {:.4f} sentences.".format(np.mean(lengths)))
    print_std(lengths)
    print("Median document length by number of sentences was {} sentences.".format(np.median(lengths)))
    print("75 percentile of document length by number of sentences was {} sentences.".format(np.percentile(lengths,
                                                                                                           75)))
    print("99 percentile of document length by number of sentences was {} sentences.".format(np.percentile(lengths,
                                                                                                           99)))

    # compare sentence length to the term_occurrence length later on.
    query = "SELECT LENGTH(sentence_text) FROM sentences ORDER BY LENGTH(sentence_text) DESC"
    text_sentences = call(pc, query)
    text_sentences = [el[0] for el in text_sentences]
    print("Longest sentence by characters was {} characters long.".format(text_sentences[0]))
    text_sentences = np.array(text_sentences)
    print("Average sentence by character length: {:.4f} characters.".format(np.mean(text_sentences)))
    print_std(text_sentences)
    print("Median sentence by character length: {} characters.".format(np.median(text_sentences)))
    print("75 percentile of sentence by character length: {} characters.".format(np.percentile(text_sentences,
                                                                                               75)))
    print("99 percentile of sentence by character length: {} characters.".format(np.percentile(text_sentences,
                                                                                               99)))

    # for tokens
    query = "SELECT sentence_text FROM sentences"
    tokens = call(pc, query)
    tokens = np.array([len(el[0].split(" ")) for el in tokens])
    print("Longest sentence by number of tokens was {} tokens.".format(np.max(tokens)))
    print("Average sentence by number of tokens was {:.4f} tokens.".format(np.mean(tokens)))
    print_std(tokens)
    print("Median sentence by number of tokens was {} tokens.".format(np.median(tokens)))
    print("75 percentile of sentence by tokens was {} tokens.".format(np.percentile(tokens, 75)))
    print("99 percentile of sentence by tokens was {} tokens.".format(np.percentile(tokens, 99)))

    # number of documents, by news outlet, distribution over time
    query = "SELECT feedName, COUNT(feedName) FROM documents " \
            "GROUP BY feedName ORDER BY COUNT(feedName) DESC"
    feed_count = call(pc, query)
    print("Number of documents per document feed:")
    pp.pprint(feed_count)
    plot_frequencies(feed_count,
                     "Outlet",
                     "Number of documents per news outlet",
                     "Outlet",
                     "# of documents",
                     "bar",
                     average=True,
                     bottom_adjust=0.25)

    query = "SELECT document_id, published FROM documents ORDER BY published"

    # tricky parse to get the date start (usually from Sunday) to Monday.
    query = "SELECT to_char(published, 'DAY') AS day_of_week, COUNT(*) day_count, " \
            "CAST (DATE_PART('DOW', published)+7 AS int) % 8 AS day_number " \
            "FROM documents GROUP BY day_of_week, day_number ORDER BY day_number ASC;"

    weekday_distribution = call(pc, query)
    pp.pprint(weekday_distribution)
    plot_frequencies(weekday_distribution,
                     "Weekday",
                     "Number of documents per weekday",
                     "Weekday",
                     "# of documents",
                     "bar",
                     average=True,
                     bottom_adjust=0.25)


    # turns out the data is only collected between May (starting on the 31st) to November (including 30th)
    query = "SELECT to_char(published, 'MONTH') AS month, COUNT(*) month_count, " \
            "DATE_PART('MONTH', published) AS month_number FROM documents " \
            "GROUP BY month, month_number order by month_number ASC"

    month_distribution = call(pc, query)
    pp.pprint(month_distribution)
    plot_frequencies(month_distribution,
                     "Month",
                     "Number of documents per month",
                     "Month",
                     "# of documents",
                     "bar",
                     average=True,
                     bottom_adjust=0.25)

    # group by week.
    query = "SELECT to_char(published, 'YYYY-WW') AS week, COUNT(*) week_count FROM documents GROUP BY week"

    week_distribution = call(pc, query)
    pp.pprint(week_distribution)
    plot_frequencies(week_distribution,
                     "Week",
                     "Number of documents per week",
                     "Week",
                     "# of documents",
                     "plot",
                     average=True,
                     bottom_adjust=0.25)

    # inspect per recorded day.
    query = "SELECT to_char(published, 'YYYY-MM-DD') AS day, COUNT(*) day_count FROM documents GROUP BY day"

    day_distribution = call(pc, query)
    plot_frequencies(day_distribution,
                     "Day",
                     "Number of documents per day",
                     "Day",
                     "# of documents",
                     "plot",
                     average=True,
                     marker='',
                     bottom_adjust=0.015)
    # quite long!
    # pp.pprint(day_distribution)

    # surprisingly, a few days have exceptionally high amounts of articles.
    query = "SELECT COUNT(*) day_count, to_char(published, 'YYYY-MM-DD') AS day FROM documents GROUP BY day " \
            "ORDER BY day_count DESC LIMIT 10"

    top_daily = call(pc, query)
    pp.pprint(top_daily)

    # investigating those, we find that those are exclusively from the WP.
    query = "SELECT feedName, COUNT(*) category_count FROM documents " \
            "WHERE to_char(published, 'YYYY-MM-DD') = '2016-08-28' " \
            "OR to_char(published, 'YYYY-MM-DD') = '2016-08-18' GROUP BY feedName"

    # there are three categories that pop out: national, politics, world.
    query = "SELECT category, COUNT(*) category_count FROM documents " \
            "WHERE (to_char(published, 'YYYY-MM-DD') = '2016-08-28' OR " \
            "to_char(published, 'YYYY-MM-DD') = '2016-08-18') AND feedName = 'WP' GROUP BY category;"

    # we can dive even deeper and see when they are coming out per hour:
    query = "SELECT DATE_PART('HOUR', published) as hour, COUNT(*) as hour_count from documents " \
            "WHERE feedName = 'WP' AND " \
            "(to_char(published, 'YYYY-MM-DD') = '2016-08-18' OR to_char(published, 'YYYY-MM-DD') = '2016-08-28') " \
            "AND (category = 'world' OR category = 'national' OR category = 'politics') GROUP BY hour;"

    # Suspecting a duplication error, we try to find the titles in every day except the two with exceptionally high
    # output.
    # SELECT d1.title, d1.feedName, to_char(d1.published, 'YYYY-MM-DD'),
    # d2.title, d2.feedName, to_char(d2.published, 'YYYY-MM-DD')
    # FROM documents d1, documents d2
    # WHERE (to_char(d1.published, 'YYYY-MM-DD') = '2016-08-18' OR to_char(d1.published, 'YYYY-MM-DD') = '2016-08-28')
    # AND d1.title = d2.title  AND to_char(d2.published, 'YYYY-MM-DD') != '2016-08-18'
    # AND to_char(d2.published, 'YYYY-MM-DD') != '2016-08-28'
    # AND d1.title != 'AP NewsAlert' AND d2.title != 'AP NewsAlert';

    # notice direct feed citations! (or duplicates!)
    query = "SELECT COUNT(*) FROM documents d1, documents d2 " \
            "WHERE d1.document_id != d2.document_id AND d1.title = d2.title;"

    citations = call(pc, query)
    # divide by two since the symmetry should be respected.
    print("Number of documents with duplicate titles: {}".format(citations[0][0]//2))

    # Interestingly, this seems to happen on a specific day more frequently than any other...
    query = "SELECT COUNT(*) FROM documents d1, documents d2 " \
            "WHERE d1.document_id != d2.document_id AND d1.title = d2.title " \
            "AND to_char(d1.published, 'YYYY-MM-DD') != to_char(d2.published, 'YYYY-MM-DD')"

    # Investigate which day it is:
    # Surprisingly, although our two weird dates lead the list, they do not account for most of these...
    query = "SELECT to_char(d1.published, 'YYYY-MM-DD') as day, COUNT(*) as day_count " \
            "FROM documents d1, documents d2 " \
            "WHERE d1.document_id != d2.document_id AND d1.title = d2.title " \
            "AND to_char(d1.published, 'YYYY-MM-DD') = to_char(d2.published, 'YYYY-MM-DD') " \
            "GROUP BY day ORDER BY day_count DESC"

    # length of sentences (per term_occurrence), with and without stopword removal
    # also length of documents per term occurrence!
    query = "SELECT document_id, COUNT(document_id) FROM term_occurrence " \
            "GROUP BY document_id ORDER BY COUNT(document_id) DESC"
    document_occurrence_count = call(pc, query)
    print("Longest document by term occurrences: {} with {} occurrences".format(document_occurrence_count[0][0],
                                                                                document_occurrence_count[0][1]))
    document_occurrence_count = np.array([el[1] for el in document_occurrence_count])
    print("Average document length by term occurrences: {:.4f} terms".format(np.mean(document_occurrence_count)))
    print("Median document length by term occurrences: {} terms".format(np.median(document_occurrence_count)))
    print("75 percentile of document length by term occurrences: {} terms"
          .format(np.percentile(document_occurrence_count, 75)))
    print("99 percentile of document length by term occurrences: {} terms"
          .format(np.percentile(document_occurrence_count, 99)))

    query = "SELECT document_id, sentence_id, COUNT(*) FROM term_occurrence " \
            "GROUP BY document_id, sentence_id ORDER BY COUNT(*) DESC"

    sentence_occurrence_count = call(pc, query)
    print("Longest sentence by term occurrences: document {} sentence {} with {} occurrences" \
          .format(sentence_occurrence_count[0][0], sentence_occurrence_count[0][1], sentence_occurrence_count[0][2]))

    sentence_occurrence_count = np.array([el[2] for el in sentence_occurrence_count])
    print("Average sentence length by term occurrences: {} terms".format(np.mean(sentence_occurrence_count)))
    print("Median sentence length by term occurrences: {} terms".format(np.median(sentence_occurrence_count)))
    print("75 percentile of sentence length by term occurrences: {} terms"
          .format(np.percentile(sentence_occurrence_count, 75)))
    print("99 percentile of sentence length by term occurrences: {} terms"
          .format(np.percentile(sentence_occurrence_count, 99)))

    # length of sentences (per entity occurrences)
    # same as above, plus the JOIN over terms WHERE is_entity = 1;

    query = "SELECT terms.term_text, COUNT(*) FROM terms, term_occurrence " \
            "WHERE terms.term_id = term_occurrence.term_id " \
            "GROUP BY terms.term_text ORDER BY COUNT(*) DESC"

    term_frequency = call(pc, query)
    process_frequencies(term_frequency, "terms")

    # same but for entities
    query = "SELECT terms.term_text, COUNT(*) FROM terms, term_occurrence " \
            "WHERE terms.term_id = term_occurrence.term_id AND terms.is_entity = true " \
            "GROUP BY terms.term_text ORDER BY COUNT(*) DESC"

    entity_frequency = call(pc, query)
    process_frequencies(entity_frequency, "entities")

    # separate plot with both.
    plt.figure()
    process_frequencies(term_frequency, "terms", hold=True)
    process_frequencies(entity_frequency, "entities", hold=True)
    plt.legend()

    # analyze entity distribution
    query = "SELECT entity_type, COUNT(*) as type_count FROM entities GROUP BY entity_type " \
            "ORDER BY entity_type ASC"

    number_entity_types = call(pc, query)
    pp.pprint(number_entity_types)

    # now factor in that some might occur more frequently, so count actual occurrences and then group.
    query = "SELECT entities.entity_type, COUNT(*) as type_count FROM entities, term_occurrence " \
            "WHERE term_occurrence.term_id = entities.entity_id GROUP BY entities.entity_type " \
            "ORDER BY entities.entity_type ASC"

    number_entity_types_occurrences = call(pc, query)
    pp.pprint(number_entity_types_occurrences)

    # do similar things for the hyperedges - as they are generated from the actual occurrences, this should yield
    # mostly the same results.
    # An analysis of clusters is also mostly useless, if we don't integrate the connection via entites/terms, as every
    # document is per definition it's own entity.
