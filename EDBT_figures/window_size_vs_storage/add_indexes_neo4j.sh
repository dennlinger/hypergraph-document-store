#!/bin/bash

neo4j stop
rm /var/lib/neo4j/data/databases/graph.db
ln -s "/data/daumiller/hypergraphs-bp/"implicit_model"/graph_5436.db" /var/lib/neo4j/data/databases/graph.db
neo4j start
sleep 5
cypher-shell -u neo4j -p neo4j "CREATE INDEX ON :Documents(document_id);"
cypher-shell -u neo4j -p neo4j "CREATE INDEX ON :Sentence(sentence_id);"
cypher-shell -u neo4j -p neo4j "CREATE INDEX ON :Term(term_id);"
cypher-shell -u neo4j -p neo4j "CREATE INDEX ON :Term(term_text);"

for window in 0 1 2 5 10 20;
do
  echo $window $folder
  neo4j stop
  rm /var/lib/neo4j/data/databases/graph.db
  ln -s "/data/daumiller/hypergraphs-bp/explicit_entity_model/graph_"$window".db" /var/lib/neo4j/data/databases/graph.db
  neo4j start
  sleep 5
  cypher-shell -u neo4j -p neo4j "CREATE INDEX ON :Documents(document_id);"
  cypher-shell -u neo4j -p neo4j "CREATE INDEX ON :Sentence(sentence_id);"
  cypher-shell -u neo4j -p neo4j "CREATE INDEX ON :Term(term_id);"
  cypher-shell -u neo4j -p neo4j "CREATE INDEX ON :Term(term_text);"

  if [ "$folder" != "implicit_model" ]; then
    cypher-shell -u neo4j -p neo4j "CREATE INDEX ON :Hyperedge(edge_id);"
  fi
done;

for window in 0 1 2 5 10;
do
  echo $window $folder
  neo4j stop
  rm /var/lib/neo4j/data/databases/graph.db
  ln -s "/data/daumiller/hypergraphs-bp/dyadic_model/graph_"$window".db" /var/lib/neo4j/data/databases/graph.db
  neo4j start
  sleep 5
  cypher-shell -u neo4j -p neo4j "CREATE INDEX ON :Documents(document_id);"
  cypher-shell -u neo4j -p neo4j "CREATE INDEX ON :Sentence(sentence_id);"
  cypher-shell -u neo4j -p neo4j "CREATE INDEX ON :Term(term_id);"
  cypher-shell -u neo4j -p neo4j "CREATE INDEX ON :Term(term_text);"

  if [ "$folder" != "implicit_model" ]; then
    cypher-shell -u neo4j -p neo4j "CREATE INDEX ON :Hyperedge(edge_id);"
  fi
done;

for window in 0 1 2 5;
do
  echo $window $folder
  neo4j stop
  rm /var/lib/neo4j/data/databases/graph.db
  ln -s "/data/daumiller/hypergraphs-bp/explicit_model/graph_"$window".db" /var/lib/neo4j/data/databases/graph.db
  neo4j start
  sleep 5
  cypher-shell -u neo4j -p neo4j "CREATE INDEX ON :Documents(document_id);"
  cypher-shell -u neo4j -p neo4j "CREATE INDEX ON :Sentence(sentence_id);"
  cypher-shell -u neo4j -p neo4j "CREATE INDEX ON :Term(term_id);"
  cypher-shell -u neo4j -p neo4j "CREATE INDEX ON :Term(term_text);"

  if [ "$folder" != "implicit_model" ]; then
    cypher-shell -u neo4j -p neo4j "CREATE INDEX ON :Hyperedge(edge_id);"
  fi
done;
