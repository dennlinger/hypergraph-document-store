-- This one restricts it
EXPLAIN (ANALYZE, COSTS, VERBOSE, BUFFERS, FORMAT JSON)
SELECT toc2.term_id, COUNT(toc2.term_id) AS frequency, t2.term_text
FROM term_occurrence as toc2,
     terms AS t2,
     (SELECT toc.document_id, toc.sentence_id-2 AS start, toc.sentence_id+2AS end, t.term_id
      FROM term_occurrence toc, terms t
      WHERE t.term_id = toc.term_id AND t.is_entity = true AND t.term_text ILIKE 'Boris Johnson') AS special
WHERE toc2.document_id = special.document_id
  AND toc2.sentence_id BETWEEN special.start AND special.end
  AND toc2.term_id != special.term_id
  AND toc2.term_id = t2.term_id
  AND t2.is_entity = true
GROUP BY toc2.term_id, t2.term_text
ORDER BY frequency DESC;
