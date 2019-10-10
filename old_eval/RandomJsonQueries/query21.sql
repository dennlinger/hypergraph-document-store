-- Query to get the most frequently occurring entities at a specific date range from implicit graph.
EXPLAIN (ANALYZE, COSTS, VERBOSE, BUFFERS, FORMAT JSON)
SELECT t.term_id, t.term_text, COUNT(t.term_id) as freq
FROM terms t, term_occurrence toc, documents d
WHERE t.term_id = toc.term_id
  AND toc.document_id = d.document_id
  AND d.published >= '2016-06-17'
  AND d.published <= '2016-06-20'
  AND t.is_entity = true
GROUP BY t.term_id, t.term_text
ORDER BY freq DESC;
