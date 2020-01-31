# Schema Definitions

### Postgres Data Store
Tables:
```
TERMS = (term_id, term_text, is_entity)
SENTENCES = (document_id -> DOCUMENTS, sentence_id, sentence_text)
DOCUMENTS = (document_id, title, feedname, category, feedurl, published)
ENTITIES = (entity_id -> TERMS, entity_type)

TERM_OCCURRENCE = ((document_id, sentence_id) -> SENTENCES, term_id -> TERMS)
```

Indexes:
If not further specified, we use the default btree of Postgres (default fillfactor is 90%)
in any subsequently defined index. Higher fillfactor is used for slightly smaller indexes,
at the cost of less flexibility when updating, which is an operation that we do not expect
for static collections.
```
terms_pkey(TERMS(term_id))
terms_term_text_gin(TERMS(term_text [gin_trgm_ops]))
sentences_pkey(SENTENCES(document_id, sentence_id))
documents_pkey(DOCUMENTS(document_id))
entities_pkey(ENTITIES(entity_id))

term_occurrence_pkey(TERM_OCCURRENCE(document_id, sentence_id, term_id))
term_occurrence_term_id(TERM_OCCURRENCE(term_id), fillfactor=100)
```

### Neo4j Data Store
Since Neo4j is storing all its properties associated to a node, we have no consistent data
model, and rather depend on having individual schemata defined, since the memory consumption is otherwise
incomparable. A minimal schema would include the following, though:

Nodes:
```
Document(document_id, title, feedname, category, feedurl, published)
Sentence(sentence_id, sentence_text)
Term(term_id, term_text,is_entity)
```
Relationships:
```
Term_in_Sentence(Term -- Sentence)
Sentence_in_Document(Sentence -- Document)
Term_in_Document(Term -- Document)
```
The last relation is necessary, since Neo4j does not support composite primary keys in its free community edition,
which is how we "circumvent" the need for an explicit relation in the Postgres schema.

Indexes:
```
:Documents(document_id);
:Sentence(sentence_id);"
:Term(term_id);"
:Term(term_text);"
```


### Explicit Model
`{w}` references the window size.
#### Postgres
Tables:
```
FULL_{w}_HYPEREDGES = (edge_id, term_id -> TERMS, pos)
FULL_{w}_HYPEREDGE_SENTENCES = (edge_id -> FULL_{w}_HYPEREDGES, (document_id, sentence_id) -> SENTENCES, pos)
FULL_{W}_HYPEREDGE_DOCUMENT = (edge_id -> FULL_{w}_HYPEREDGES, document_id -> DOCUMENTS)
```

Indexes:
```
full_hyperedges_pkey(FULL_{w}_HYPEREDGES(edge_id, term_id, pos))
full_hyperedges_term_id(FULL_{w}_HYPEREDGES(term_id), fillfactor=100)
full_hyperedge_sentences_pkey(FULL_{w}_HYPEREDGE_SENTENCES(edge_id, document_id, sentence_id, pos))
full_hyperedge_document_pkey(FULL_{w}_HYPEREDGE_DOCUMENT(edge_id, document_id))
```

#### Neo4j
For the sake of simplicity, we utilize the theoretical shared model for the data store
as outlined above, and only define additional tables and relationships.
Nodes:
```
Hyperedge(edge_id)
```
Relationships:
```
Term_in_Edge(Term -- Hyperedge, pos)
Sentence_in_Edge(Sentence -- Hyperedge)
Document_in_Edge(Document -- Hyperedge)
```

Indexes:
```
:Hyperedge(edge_id);
```

### Explicit Entity Model

#### Postgres
Tables:
```
ENTITY_{w}_HYPEREDGES = (edge_id, term_id -> TERMS, pos)
ENTITY_{w}_HYPEREDGE_SENTENCES = (edge_id -> ENTITY_{w}_HYPEREDGES, (document_id, sentence_id) -> SENTENCES, pos)
ENTITY_{W}_HYPEREDGE_DOCUMENT = (edge_id -> ENTITY_{w}_HYPEREDGES, document_id -> DOCUMENTS)
```
Indexes:
```
entity_hyperedges_pkey(ENTITY_{w}_HYPEREDGES(edge_id, term_id, pos))
entity_hyperedges_term_id(ENTITY_{w}_HYPEREDGES(term_id), fillfactor=100)
entity_hyperedge_sentences_pkey(ENTITY_{w}_HYPEREDGE_SENTENCES(edge_id, document_id, sentence_id, pos))
entity_hyperedge_document_pkey(ENTITY_{w}_HYPEREDGE_DOCUMENT(edge_id, document_id))
```

#### Neo4j
Nodes:
```
Entity_Hyperedge(edge_id)
```
Relationships:
```
Term_in_Edge(Term -- Entity_Hyperedge, pos)
Sentence_in_Edge(Sentence -- Entity_Hyperedge)
Document_in_Edge(Document -- Entity_Hyperedge)
```

Indexes:
```
:Entity_Hyperedge(edge_id);
```

### Implicit Model

#### Postgres
No additional tables are required in Postgres.

#### Neo4j
No additional nodes or relationships are required in Neo4j.

### Implicit Entity Model

#### Postgres
No additional tables are required in Postgres.


#### Neo4j
No additional nodes or relationships are required in Neo4j.


### Dyadic Entity Model

#### Postgres
Tables:
```
ENTITY_{w}_DYADIC = (edge_id, source_id -> TERMS, target_id -> TERMS, pos)
```
While strictly speaking not a foreign key, we derive the `edge_id`s from the definition
of our hypergraph, since the dyadic table can be generated from the hyperedge table.
The specific query for creating the reduction in Postgres is
```
CREATE TABLE ENTITY_{w}_DYADIC AS
      (SELECT eh1.edge_id as edge_id, eh1.term_id as source_id, eh2.term_id as target_id, ABS(eh1.pos - eh2.pos) AS pos
       FROM entity_{w}_hyperedges as eh1, entity_{w}_hyperedges as eh2
       WHERE eh1.edge_id = eh2.edge_id
         AND eh1.term_id != eh2.term_id)
```
Further, we use the same `ENTITY_{w}_HYPEREDGE_SENTENCES` and `ENTITY_{w}_HYPEREDGE_DOCUMENT`
tables as defined in the explicit entity model.

Indexes:
```
entity_dyadic_pkey(ENTITY_{w}_DYADIC(edge_id, source_id, target_id))
entity_dyadic_source_id(ENTITY_{w}_DYADIC(source_id), fillfactor=100)
```

#### Neo4j
Nodes:
```
Entity_Hyperedge(edge_id)
```
Relationships:
```
Term_in_Term(Term -- Term, pos)
Sentence_in_Edge(Sentence -- Entity_Hyperedge)
Document_in_Edge(Document -- Entity_Hyperedge)
```

Indexes:
```
:Entity_Hyperedge(edge_id);
```
