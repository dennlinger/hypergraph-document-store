-- Document frequency of a node, based on hypergraph
EXPLAIN (ANALYZE, COSTS, VERBOSE, BUFFERS, FORMAT JSON)
SELECT distinct_count.term_text, COUNT(distinct_count.term_text) as freq
FROM (SELECT t.term_text, ehd.document_id
      FROM entity_hyperedges eh, terms t, entity_hyperedge_document ehd
      WHERE eh.edge_id = ehd.edge_id
        AND eh.term_id = t.term_id
      GROUP BY t.term_text, ehd.document_id) as distinct_count
GROUP BY distinct_count.term_text
ORDER BY freq DESC;
