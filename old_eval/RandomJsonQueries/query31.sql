-- dyadic queries Trump
EXPLAIN (ANALYZE, COSTS, VERBOSE, BUFFERS, FORMAT JSON)
SELECT ed.target_id, COUNT(ed.target_id) AS frequency, t2.term_text
FROM entity_dyadic AS ed, terms t, terms AS t2
WHERE ed.source_id = t.term_id
  AND t.term_text ILIKE 'Donald Trump'
  AND ed.target_id = t2.term_id
GROUP BY ed.target_id, t2.term_text
ORDER BY frequency DESC;
