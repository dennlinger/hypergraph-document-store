"""
Attempt at a first template script to evaluate runtimes for the implicit model in Neo4j.
"""

import subprocess
import json
import time


if __name__ == "__main__":
    print("Evaluation for Implicit Model")
    fn = "./entities.json"
    with open(fn) as f:
        data = json.load(f)

    subprocess.run(["neo4j", "stop"])
    subprocess.run(["rm", "/var/lib/neo4j/data/databases/graph.db"])
    subprocess.run(["ln", "-s", "/data/daumiller/hypergraphs-bp/implicit_model/graph_5436.db",
                    "/var/lib/neo4j/data/databases/graph.db"])
    subprocess.run(["neo4j", "start"])
    time.sleep(5)

    for window in [0, 1, 2, 5, 10, 20]:

        print("", flush=True)  # Dummy for proper carriage return
        print("Starting with window size {}.".format(window), flush=True)
        for iteration in range(6):
            print("", flush=True)  # Dummy for proper carriage return
            print("Starting with iteration {}".format(iteration), flush=True)
            print("", flush=True)  # Dummy for proper carriage return

            for i, (entity_label, properties) in enumerate(data.items()):
                print("Entity: {}/{}\t".format(i+1, len(data)), end="", flush=True)
                query = "PROFILE MATCH (t:Term {{term_text: '{}'}})-[:T_IN_S]-(sentence)-[:S_IN_D]-(document)-[:S_IN_D]-(co_sentence)-[m:T_IN_S]-(term) " \
                        "where co_sentence.sentence_id in range(sentence.sentence_id-{}, sentence.sentence_id+{}) " \
                        "return term.term_text As text, count(m) AS score order by score desc;".format(entity_label, window, window)
                out = subprocess.check_output(["cypher-shell", "-u", "neo4j", "-p", "neo4j", query])

                # clean data to extract float
                # sample: (b'Time: 6\n')
                start_ind = out.find(b"Time: ")
                time_taken = float(out[start_ind+6:start_ind+12].split(b"\n")[0])
                print("{}\r".format(time_taken), end="", flush=True)

                if iteration > 0:  # take one round of cache warm-up
                    times = data[entity_label].get("implicit_neo4j", {})

                    window_times = times.get(str(window), [])
                    window_times.append(time_taken)
                    times[str(window)] = window_times
                    data[entity_label]["implicit_neo4j"] = times

    with open(fn, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
