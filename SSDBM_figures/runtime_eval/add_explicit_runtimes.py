"""
Attempt at a first template script to evaluate runtimes for the explicit model in Postgres.
"""

from PostgresConnector_EDBT import PostgresConnector
import json


if __name__ == "__main__":
    print("Evaluation for Full Explicit Model")
    fn = "./entities.json"
    with open(fn) as f:
        data = json.load(f)

    pc = PostgresConnector(port=5436)

    for window in [0, 1, 2, 5]:
        print("", flush=True)  # Dummy for proper carriage return
        print("Starting with window size {}.".format(window), flush=True)
        for iteration in range(7):
            print("", flush=True)  # Dummy for proper carriage return
            print("Starting with iteration {}".format(iteration), flush=True)
            print("", flush=True)  # Dummy for proper carriage return

            for i, (entity_label, properties) in enumerate(data.items()):
                print("Entity: {}/{}\t".format(i+1, len(data)), end="", flush=True)
                query = """
                EXPLAIN ANALYZE
                WITH s AS (SELECT term_id FROM terms
                           WHERE term_text = '{}'),
                     q AS (SELECT edge_id FROM full_{}_hyperedges eh
                           WHERE eh.term_id = (SELECT s.term_id FROM s))
                SELECT term_text, counts.freq FROM terms t,
                      (SELECT term_id, COUNT(*) as freq
                       FROM full_{}_hyperedges eh
                       WHERE eh.edge_id = ANY(ARRAY(SELECT * FROM q))
                       GROUP BY term_id ORDER BY freq DESC) as counts
                WHERE counts.term_id = t.term_id
                  AND counts.term_id != (SELECT term_id FROM s);""".format(entity_label, window, window)

                with pc as opc:
                    opc.cursor.execute(query)
                    res = opc.cursor.fetchall()
                    if not res[-1][0].lower().startswith("execution time:"):
                        print("")
                        print(res, flush=True)
                        print("")
                    else:
                        # clean data to extract float
                        # sample: ('Execution Time: 1352.866 ms',)
                        time_taken = float(res[-1][0].split(":")[1].strip().split(" ")[0])
                        print("{}\r".format(time_taken), end="", flush=True)

                if iteration > 0:  # take one round of cache warm-up
                    times = data[entity_label].get("explicit", {})

                    window_times = times.get(str(window), [])
                    window_times.append(time_taken)
                    times[str(window)] = window_times
                    data[entity_label]["explicit"] = times

    with open(fn, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
