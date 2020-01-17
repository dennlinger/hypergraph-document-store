# Query Implementations

## Used Queries
We detail the exact queries for both PostgreSQL and Neo4j that were used for the respective models. Note that these are dependent on the specific implementations.
For both Postgres and Neo4j, we use the same set of entities as evaluation metric, and give both systems a complete iteration across all entities as cache-warmup.

For Postgres, we further chose optimizations based on the query tree, which significantly altered the evaluation runtimes, specifically when not using CTE.

### Explicit Model

#### Postgres:
`{ent}` refers to the evaluated entity;
`{w}` refers to the window size.

```SQL
EXPLAIN ANALYZE
WITH s AS (SELECT term_id FROM terms
           WHERE term_text = '{ent}'),
     q AS (SELECT edge_id
           FROM full_{w}_hyperedges eh
           WHERE eh.term_id = (SELECT s.term_id FROM s))
SELECT term_text, counts.freq FROM terms t,
      (SELECT term_id, COUNT(*) AS freq
       FROM full_{w}_hyperedges eh
       WHERE eh.edge_id = ANY(ARRAY(SELECT * FROM q))
       GROUP BY term_id ORDER BY freq DESC) AS counts
WHERE counts.term_id = t.term_id
  AND counts.term_id != (SELECT term_id FROM s);
```

#### Neo4j:
Note that window sizes were evaluated across different collections in Neo4j, which is why we do not refere to a specific hyperedge table. Obviously
```SQL
PROFILE MATCH (t:Term {{term_text: '{ent}'}})-[:T_IN_E]-
              (hyperedge)-[m:T_IN_E]-(term)
RETURN term.term_text AS text,
       count(m) AS score
ORDER BY score DESC;
```

### Explicit Entity Model

#### Postgres:
```SQL
EXPLAIN ANALYZE
WITH s AS (SELECT term_id FROM terms
           WHERE term_text = '{ent}'),
     q AS (SELECT edge_id FROM entity_{}_hyperedges eh
           WHERE eh.term_id = (SELECT s.term_id FROM s))
SELECT term_text, counts.freq FROM terms t,
      (SELECT term_id, COUNT(*) AS freq
       FROM entity_{w}_hyperedges eh
       WHERE eh.edge_id = ANY(ARRAY(SELECT * FROM q))
       GROUP BY term_id
       ORDER BY freq DESC) AS counts
WHERE counts.term_id = t.term_id
  AND counts.term_id != (SELECT term_id FROM s);
```

#### Neo4j:
Again, Neo4j implementations make use of different containers for different window sizes.
```SQL
PROFILE MATCH (t:Term {{term_text: '{ent}'}})-[:T_IN_E]-
              (entity_hyperedge)- [m:T_IN_E]-(term)
RETURN term.term_text AS text,
       count(m) AS score
ORDER BY score DESC;
```

### Implicit Model

#### Postgres:
```SQL
EXPLAIN ANALYZE
WITH s AS (SELECT term_id FROM terms
           WHERE term_text = '{ent}'),
     q AS (SELECT toc.document_id,
                  toc.sentence_id - {w} AS start,
                  toc.sentence_id + {w} AS end
           FROM term_occurrence toc
           WHERE toc.term_id = (SELECT s.term_id FROM s))
SELECT term_text, counts.freq FROM terms t,
       (SELECT term_id, COUNT(*) AS freq
        FROM term_occurrence toc, q
        WHERE toc.document_id = q.document_id
          AND toc.sentence_id BETWEEN q.start AND q.end
        GROUP BY toc.term_id) AS counts
WHERE counts.term_id = t.term_id
  AND counts.term_id != (SELECT term_id FROM s)
ORDER BY counts.freq DESC;
```

#### Neo4j:
```SQL
PROFILE MATCH (t:Term {{term_text: '{ent}'}})-[:T_IN_S]-
              (sentence)-[:S_IN_D]-(document)-[:S_IN_D]-
              (co_sentence)-[m:T_IN_S]-(term)
WHERE co_sentence.sentence_id
   IN range(sentence.sentence_id-{w}, sentence.sentence_id+{w})
RETURN term.term_text AS text, count(m) AS score
ORDER BY score DESC;
```

### Implicit Entity Model

#### Postgres:
```SQL
EXPLAIN ANALYZE
WITH s AS (SELECT term_id FROM terms
           WHERE term_text = '{ent}'),
     q AS (SELECT toc.document_id,
                  toc.sentence_id - {w} AS start,
                  toc.sentence_id + {w} AS end
           FROM term_occurrence toc
           WHERE toc.term_id = (SELECT s.term_id FROM s))
SELECT term_text, counts.freq FROM terms t,
       (SELECT term_id, COUNT(*) AS freq
        FROM term_occurrence toc, q
        WHERE toc.document_id = q.document_id
          AND toc.sentence_id BETWEEN q.start AND q.end
        GROUP BY toc.term_id) AS counts
WHERE counts.term_id = t.term_id
  AND t.is_entity = true
  AND counts.term_id != (SELECT term_id FROM s)
ORDER BY counts.freq DESC;
```

#### Neo4j:
```SQL
PROFILE MATCH (t:Term {{term_text: '{ent}'}})-[:T_IN_S]-
              (sentence)-[:S_IN_D]-(document)-[:S_IN_D]-
              (co_sentence)-[m:T_IN_S]-(term)
WHERE co_sentence.sentence_id
   IN range(sentence.sentence_id-{w}, sentence.sentence_id+{w})
  AND term.is_entity = 'True'
RETURN term.term_text AS text, count(m) AS score
ORDER BY score DESC;
```

### Dyadic Entity Model

#### Postgres:

```SQL
EXPLAIN ANALYZE
WITH s AS (SELECT term_id FROM terms
           WHERE term_text = '{ent}'),
     q AS (SELECT ed.target_id FROM entity_{w}_dyadic ed
           WHERE ed.source_id = (SELECT s.term_id FROM s))
SELECT t.term_text, counts.freq FROM terms t,
       (SELECT target_id, COUNT(*) AS freq FROM q
        GROUP BY target_id
        ORDER BY freq DESC) AS counts
WHERE counts.target_id = t.term_id
  AND counts.target_id != (SELECT term_id FROM s);
```

#### Neo4j:

```SQL
PROFILE MATCH (t:Term {{term_text: '{ent}'}})-[m:T_IN_T]-(term)
RETURN term.term_text AS text,
count(m) AS score
ORDER BY score DESC;
```
