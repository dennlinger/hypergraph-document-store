#!/bin/bash

for port in 5435 5436 5437 5438 5439;
do
  for folder in implicit_model explicit_model explicit_entity_model dyadic_model;
  do
    echo $port $folder
    neo4j stop
    rm /var/lib/neo4j/data/databases/graph.db
    ln -s "/data1/daumiller/hypergraphs-bp/"$folder"/graph_"$port".db" /var/lib/neo4j/data/databases/graph.db
    neo4j start
    sleep 5
    cypher-shell -u neo4j -p neo4j "CREATE INDEX ON :Documents(document_id);"
    cypher-shell -u neo4j -p neo4j "CREATE INDEX ON :Sentences(sentence_id);"
    cypher-shell -u neo4j -p neo4j "CREATE INDEX ON :Terms(term_id);"
    cypher-shell -u neo4j -p neo4j "CREATE INDEX ON :Terms(term_text);"

    if [ "$folder" != "implicit_model" ]; then
      cypher-shell -u neo4j -p neo4j "CREATE INDEX ON :Hyperedge(edge_id);"
    fi
  done;
done;
