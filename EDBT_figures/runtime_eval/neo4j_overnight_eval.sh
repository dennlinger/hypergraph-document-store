#!/bin/bash

/home/daumiller/anaconda3/bin/python3.7 neo4j_add_explicit_entity_runtimes.py
/home/daumiller/anaconda3/bin/python3.7 neo4j_add_implicit_runtimes.py
/home/daumiller/anaconda3/bin/python3.7 neo4j_add_explicit_runtimes.py
/home/daumiller/anaconda3/bin/python3.7 neo4j_add_dyadic_entity_runtimes.py
/home/daumiller/anaconda3/bin/python3.7 neo4j_add_implicit_entity_runtimes.py
