-- Document degree of a node, based on implicit
EXPLAIN (ANALYZE, COSTS, VERBOSE, BUFFERS, FORMAT JSON)
SELECT distinct_count.term_text, COUNT(distinct_count.term_text) as freq
FROM (SELECT t.term_text, toc.document_id
      FROM term_occurrence toc, terms t
      WHERE t.term_id = toc.term_id
        AND t.is_entity = true
      GROUP BY t.term_id, t.term_text, toc.document_id) AS distinct_count
GROUP BY distinct_count.term_text
ORDER BY freq DESC;
