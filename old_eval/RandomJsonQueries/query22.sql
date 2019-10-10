-- Do the same via the hyperedges
EXPLAIN (ANALYZE, COSTS, VERBOSE, BUFFERS, FORMAT JSON)
SELECT t.term_id, t.term_text, COUNT(t.term_id) as freq
FROM entity_hyperedges eh, entity_hyperedge_document ehd, terms t, documents d
WHERE eh.term_id = t.term_id
  AND eh.edge_id = ehd.edge_id
  AND d.document_id = ehd.document_id
  AND d.published >= '2016-06-17'
  AND d.published <= '2016-06-20'
GROUP BY t.term_id, t.term_text
ORDER BY freq DESC;
