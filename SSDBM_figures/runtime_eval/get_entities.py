"""
Gets n entities and their respective degrees.
"""

from PostgresConnector_SSDBM import PostgresConnector
import numpy as np
import json

if __name__ == "__main__":

    pc = PostgresConnector(port=5436)

    with pc as opc:
        # noinspection SqlNoDataSourceInspection
        opc.cursor.execute("SELECT t.term_text, COUNT(*) as degree "
                           "FROM terms t, term_occurrence toc "
                           "WHERE t.term_id = toc.term_id "
                           "  AND t.is_entity = true "
                           "GROUP BY t.term_text, t.term_id")

        res = opc.cursor.fetchall()

    np.random.seed(3019)
    indices = np.random.choice(len(res), 3000, replace=False)
    formatted = {}
    for idx in indices:
        if len(formatted) >= 1990:
            break

        # "proper sanitizing", they said
        if "'" in res[idx][0]:
            continue
        else:
            key = res[idx][0]
        formatted[key] = {"degree": res[idx][1]}

    # adding manually 10 highly relevant terms
    formatted["Hillary Clinton"] = {"degree": 58778}
    formatted["London"] = {"degree": 15540}
    formatted["North Carolina"] = {"degree": 5742}
    formatted["CBS News"] = {"degree": 4120}
    formatted["Asia"] = {"degree": 2957}
    formatted["Conservative Party (UK)"] = {"degree": 2347}
    formatted["2016-FA"] = {"degree": 2022}
    formatted["Nigeria"] = {"degree": 1828}
    formatted["Jill Stein"] = {"degree": 1811}
    formatted["2016-09-07"] = {"degree": 1270}

    with open("entities.json", "w") as f:
        json.dump(formatted, f, indent=2, ensure_ascii=False)
