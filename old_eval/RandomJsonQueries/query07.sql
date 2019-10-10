-- Boris Johnson
-- Query to extract the most frequently co-occurring terms together with "Boris Johnson"
-- Based on the extraction from the generated hypergraph.
EXPLAIN (ANALYZE, COSTS, VERBOSE, BUFFERS, FORMAT JSON)
SELECT eh2.term_id, COUNT(eh2.term_id) AS frequency, t2.term_text
FROM entity_hyperedges AS eh2,
     (SELECT eh.edge_id, eh.term_id
      FROM entity_hyperedges eh, terms t
      WHERE t.term_id = eh.term_id AND t.term_text ILIKE 'Boris Johnson') AS special,
     terms AS t2
WHERE eh2.term_id = t2.term_id
  AND eh2.edge_id = special.edge_id
  AND eh2.term_id != special.term_id
GROUP BY eh2.term_id, t2.term_text
ORDER BY frequency DESC;
