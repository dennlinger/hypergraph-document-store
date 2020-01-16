"""
Briefly check distribution of degrees to see if it makes sense.
"""

from collections import Counter
import json

if __name__ == "__main__":

    with open("entities.json") as f:
        data = json.load(f)

    c= Counter([v["degree"] for k, v in data.items()])
    print(sorted(c.items(), key=lambda tup: tup[0]))
