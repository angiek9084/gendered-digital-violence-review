# Gendered Digital Violence Review

Private research repository for bibliographic enrichment and eligibility screening (2016–2026).

## Current batch
160 publications require external metadata checks. The 249 thematically accepted records and 38 records reserved for human screening are not part of this batch.

## Run
1. Upload `data/cola_160_openalex_crossref.csv` (160 records; columns `record_id,title,doi,year,document_type`).
2. Under **Settings → Secrets and variables → Actions**, create the repository secret `OPENALEX_API_KEY`. Optional: `CONTACT_EMAIL`.
3. Open **Actions → Enriquecer 160 publicaciones → Run workflow**.
4. Download the private artifact `enriquecimiento-api-160` from the run.

Results include Crossref/OpenAlex title matches, similarity scores, abstracts, links and error fields. **Metadata matches do not establish eligibility**. Verify the studied population and substantive focus before deciding.

Never commit API keys, passwords, or unlicensed full texts.
