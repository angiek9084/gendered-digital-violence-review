# Data dictionary

## `bibliographic_corpus_350.csv`
- `record_id`: stable internal identifier used across the 350-document corpus.
- `publication_year`: publication year in reconciled source records.
- `title`: publication title as standardized in the source master list.
- `doi`: DOI where reported; blank where unavailable.
- `authors_as_exported`: author string from Scopus / Web of Science, potentially abbreviated; blank for records lacking an individual author.
- `source_title`: publication source or venue as recorded in the source master list.
- `document_type_as_exported`: original category label from the bibliographic exports (not harmonized by this CSV).
- `original_database`: Scopus and/or Web of Science source labels.

## Figure data
- `documents` / `publications`: counts of included records.
- `percentage`: percent of 350 unless otherwise specified.
- `country`: author's affiliated country, using full counting; the table excludes missing-affiliation documents.
- `frequency`: number of keyword occurrences/records under the normalized bibliometric keyword procedure; keywords may co-occur.
- `share_of_individual_first_authors_pct`: share among the 341 records with individually classified first authors, excluding institutional authorships.

## Privacy and provenance
The public data include publication metadata and **aggregate** first-author classification only. They omit individual-level inferred gender coding and public-profile URLs. This prevents a potentially misleading impression of confirmed gender identity for named persons.
