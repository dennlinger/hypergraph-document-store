-- The entitiy's occurrence count, by week.
EXPLAIN (ANALYZE, COSTS, VERBOSE, BUFFERS, FORMAT JSON)
SELECT to_char(published, 'YYYY-WW') AS week, COUNT(*) week_count
FROM (
  SELECT doc.published
  FROM term_occurrence as toc, terms as t, documents as doc
  WHERE toc.term_id = t.term_id
    AND t.term_text ILIKE 'Boris Johnson'
    AND toc.document_id = doc.document_id) as johnson_documents
GROUP BY week;
