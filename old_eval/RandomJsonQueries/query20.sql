-- or explicit on entity hyperedges
EXPLAIN (ANALYZE, COSTS, VERBOSE, BUFFERS, FORMAT JSON)
SELECT to_char(published, 'YYYY-WW') AS week, COUNT(*) week_count
FROM (
  SELECT doc.published
  FROM entity_hyperedges as eh, entity_hyperedge_document as ehd, documents as doc, terms t
  WHERE eh.edge_id = ehd.edge_id
    AND t.term_id = eh.term_id
    AND t.term_text ILIKE '2016-07-19'
    AND ehd.document_id = doc.document_id) as special_documents
GROUP BY week;
