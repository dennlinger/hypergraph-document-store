-- Occurrence frequency of a node, based on hypergraph
EXPLAIN (ANALYZE, COSTS, VERBOSE, BUFFERS, FORMAT JSON)
SELECT t.term_text, COUNT(t.term_text) as freq
FROM entity_hyperedges eh, terms t
WHERE eh.term_id = t.term_id
GROUP BY t.term_id, t.term_text
ORDER BY freq DESC;
