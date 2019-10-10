-- Implementation of the weighted degree centrality on hypergraph
EXPLAIN (ANALYZE, COSTS, VERBOSE, BUFFERS, FORMAT JSON)
SELECT t.term_text, SUM(weights.weight) as total
FROM entity_hyperedges eh, terms t,
     (SELECT edge_id, 1.0/COUNT(edge_id) as weight
      FROM entity_hyperedges
      GROUP BY edge_id) as weights
WHERE eh.edge_id = weights.edge_id
  AND eh.term_id = t.term_id
GROUP BY t.term_text
ORDER BY total DESC;
