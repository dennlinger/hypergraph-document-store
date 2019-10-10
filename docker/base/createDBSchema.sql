-- File to set up the schema prior to running any of the local hyppograph files.
--
-- The structure will be as follows:
--
--   VertexTable: Contains the basic information on the vertices, i.e. 

-- EntitiyMetaTable
-- TermTable
-- ArticleTable
-- SentenceInArticleTable
-- TermOccurrenceTable
-- TermMetaTable

-- Start with basic setup, and then extend later:
-- Terms basically store just an identifier.
-- Maybe extend with isEntity bit flag?
CREATE TABLE terms (
	term_id integer,
	term_text varchar(127),
	is_entity boolean,
	PRIMARY KEY (term_id)
);

-- Document collection
-- Arguments are basically straight from the MongoDB.
CREATE TABLE documents (
	document_id integer,
	title text,
	feedName varchar(20),
	category varchar(20),
	feedURL text,
	published timestamp,
	PRIMARY KEY (document_id)
);

-- Sentences are related to documents (later), but for now store the whole sentence just as that.
CREATE TABLE sentences (
	document_id integer,
	sentence_id integer,
	sentence_text text,
	PRIMARY KEY (document_id, sentence_id),
	FOREIGN KEY (document_id) REFERENCES documents (document_id)
	ON DELETE CASCADE
);
	
-- Terms occur in sentences
-- think about whether a term should be listed multiple times for the same sentences,
-- since for now this is NOT the case!
-- This would require an additional identifier/value here.
CREATE TABLE term_occurrence (
	document_id integer,
	sentence_id integer,
	term_id integer,
	PRIMARY KEY (document_id, sentence_id, term_id),
	FOREIGN KEY (document_id, sentence_id) REFERENCES sentences (document_id, sentence_id)
	ON DELETE CASCADE,
    FOREIGN KEY (term_id) REFERENCES terms (term_id)
    ON DELETE CASCADE
);
	
-- Entity meta data (to be extended)
-- Here it is important to note that the *existing* entity meta data is with respect to
-- specific _OCCURRENCES_, not actual entities themselves.
-- This is why we cannot use a lot of the available information from MongoDB like with the
-- previous article collection. Instead, it would have to be modeled and adopted to specific
-- occurrences (i.e. put those values in the term_occurrence table).
-- For the speed of use, maybe consider a term_occurrence_meta table, that stores additional
-- information, with the foreign key to a term_occurrence (would require specific identifier!).
CREATE TABLE entities (
	entity_id integer,
	entity_type varchar(4),
	PRIMARY KEY (entity_id),
	FOREIGN KEY (entity_id) REFERENCES terms (term_id)
	ON DELETE CASCADE
);

-- next step is to include hyperedges.
-- This will be generated from the values already present, so we can more or less directly work
-- with the values present there.
-- Maybe explicitly store the sentence ID as well, so we can easily cut down the number of edges
-- we have to search for. Currently, this is impossible to link, or at least very expensive!
CREATE TABLE hyperedges (
	edge_id integer,
	term_id integer,
	pos integer,
	PRIMARY KEY (edge_id, term_id, pos),
	FOREIGN KEY (term_id) REFERENCES terms (term_id)
	ON DELETE CASCADE
);

-- hyperedge storage for the number of vertices in it,
-- table where we store the sentences
-- table where we store the documents all separate
CREATE TABLE hyperedge_document (
	edge_id integer,
	document_id integer,
	PRIMARY KEY (edge_id, document_id),
	FOREIGN KEY (document_id) REFERENCES documents (document_id)
	ON DELETE CASCADE
);

CREATE TABLE hyperedge_sentences (
	edge_id integer,
	document_id integer,
	sentence_id integer,
	pos integer,
	PRIMARY KEY (edge_id, document_id, sentence_id, pos),
	FOREIGN KEY (document_id, sentence_id) REFERENCES sentences (document_id, sentence_id)
	ON DELETE CASCADE
);


