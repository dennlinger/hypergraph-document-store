-- Or the explicit version of that
EXPLAIN (ANALYZE, COSTS, VERBOSE, BUFFERS, FORMAT JSON)
SELECT to_char(published, 'YYYY-WW') AS week, COUNT(*) week_count
FROM (
  SELECT doc.published
  FROM hyperedges as h, hyperedge_document as hd, documents as doc, terms t
  WHERE h.edge_id = hd.edge_id
    AND t.term_id = h.term_id
    AND t.term_text ILIKE '2016-07-19'
    AND hd.document_id = doc.document_id) as special_documents
GROUP BY week;
