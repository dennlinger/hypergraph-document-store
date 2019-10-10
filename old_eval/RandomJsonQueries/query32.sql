-- dyadic by week Trump
EXPLAIN (ANALYZE, COSTS, VERBOSE, BUFFERS, FORMAT JSON)
SELECT to_char(published, 'YYYY-WW') AS week, COUNT(*) week_count
FROM (
  SELECT doc.published
  FROM entity_dyadic as ed, entity_hyperedge_document as ehd, documents as doc, terms t
  WHERE ed.edge_id = ehd.edge_id
    AND t.term_id = ed.source_id
    AND t.term_text ILIKE 'Donald Trump'
    AND ehd.document_id = doc.document_id) as trump_documents
GROUP BY week;
