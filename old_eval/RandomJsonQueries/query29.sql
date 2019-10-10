-- Implicit calculation across ALL:
EXPLAIN (ANALYZE, COSTS, VERBOSE, BUFFERS, FORMAT JSON)
SELECT t3.term_text, SUM(edge_weights.edge) as total_weight
FROM term_occurrence toc3, terms t3,
      (SELECT toc.document_id, toc.sentence_id, toc.term_id, 1.0/SUM(weight.ents) as edge
       FROM term_occurrence toc, terms t,
           (SELECT toc2.document_id, toc2.sentence_id, COUNT(*) as ents
            FROM term_occurrence toc2, terms t2
            WHERE toc2.term_id = t2.term_id
              AND t2.is_entity = true
            GROUP BY toc2.document_id, toc2.sentence_id) as weight
       WHERE toc.document_id = weight.document_id
         AND ABS(toc.sentence_id - weight.sentence_id) <= 2
         AND toc.term_id = t.term_id
         AND t.is_entity = true
       GROUP BY toc.document_id, toc.sentence_id, toc.term_id) as edge_weights
WHERE toc3.term_id = t3.term_id
  AND t3.is_entity = true
  AND toc3.document_id = edge_weights.document_id
  AND toc3.sentence_id = edge_weights.sentence_id
  AND toc3.term_id = edge_weights.term_id
GROUP BY t3.term_text
ORDER BY total_weight DESC;
-- ggf replace the 1st inner where we do something like SUM(weight.ents)/COUNT(*), since we count multiple,
-- and then instead don't
