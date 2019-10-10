-- Implementation of the weighted degree centrality on implicit network
-- for a specific node
EXPLAIN (ANALYZE, COSTS, VERBOSE, BUFFERS, FORMAT JSON)
SELECT SUM(big.freq)
FROM (SELECT 1.0/COUNT(*) as freq
      FROM term_occurrence toc, terms t,
           (SELECT toc2.document_id, toc2.sentence_id, t2.term_id
            FROM term_occurrence toc2, terms t2
            WHERE toc2.term_id = t2.term_id AND t2.term_text ILIKE 'Donald Trump') as special
      WHERE toc.document_id = special.document_id
        AND ABS(toc.sentence_id - special.sentence_id) <= 2
        AND toc.term_id = t.term_id AND t.is_entity = true
      GROUP BY special.document_id, special.sentence_id) as big;
