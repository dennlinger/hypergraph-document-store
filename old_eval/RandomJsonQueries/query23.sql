-- Occurrence degree of a node, based on implicit
EXPLAIN (ANALYZE, COSTS, VERBOSE, BUFFERS, FORMAT JSON)
SELECT t.term_text, COUNT(t.term_id) as freq
FROM term_occurrence toc, terms t
WHERE t.term_id = toc.term_id
  AND t.is_entity = true
GROUP BY t.term_id, t.term_text
ORDER BY freq DESC;
