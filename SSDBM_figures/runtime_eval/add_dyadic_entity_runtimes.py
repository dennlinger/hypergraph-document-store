"""
Attempt at a first template script to evaluate runtimes for the dyadic_entity model in Postgres.
"""

from PostgresConnector_SSDBM import PostgresConnector
import json


if __name__ == "__main__":
    print("Evaluation for Dyadic Entity Model")
    fn = "./entities.json"
    with open(fn) as f:
        data = json.load(f)

    pc = PostgresConnector(port=5436)

    for window in [0, 1, 2, 5, 10]:
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
                     q AS (SELECT ed.target_id FROM entity_{}_dyadic ed
                           WHERE ed.source_id = (SELECT s.term_id FROM s))
                SELECT t.term_text, counts.freq FROM terms t,
                      (SELECT target_id, COUNT(*) AS freq FROM q
                       GROUP BY target_id ORDER BY freq DESC) as counts
                WHERE counts.target_id = t.term_id
                  AND counts.target_id != (SELECT term_id FROM s);""".format(entity_label, window)

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
                    times = data[entity_label].get("dyadic_entity", {})

                    window_times = times.get(str(window), [])
                    window_times.append(time_taken)
                    times[str(window)] = window_times
                    data[entity_label]["dyadic_entity"] = times

    with open(fn, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
