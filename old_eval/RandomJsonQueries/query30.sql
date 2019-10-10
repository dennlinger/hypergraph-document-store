-- created with VIEWs:
EXPLAIN (ANALYZE, COSTS, VERBOSE, BUFFERS, FORMAT JSON)
SELECT t.term_text, SUM(sw.weight) total
FROM term_occurrence toc, terms t, sentence_weights sw
WHERE toc.term_id = t.term_id
  AND t.is_entity = true
  AND toc.document_id = sw.document_id
  AND toc.sentence_id = sw.sentence_id
GROUP BY t.term_text
ORDER BY total DESC;
