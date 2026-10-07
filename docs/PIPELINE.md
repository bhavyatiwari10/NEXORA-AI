# Nexora AI Pipeline Contract

| Stage | Input | Output | Testable boundary |
|---|---|---|---|
| Ingest | platform payload | normalized messages | webhook tests |
| Extract | conversation | structured extraction | LLM parser tests |
| Validate | extraction | validation report | Pydantic tests |
| Resolve | entities | matched customer/product | fuzzy-match tests |
| Persist | validated data | database records | repository/API tests |
| Order | order intent | order + items | order-flow tests |
| Finance | order | GST totals + invoice | GST/PDF tests |
| Follow-up | intent/time | reminder | scheduler tests |
| Analytics | natural language | safe query spec | query-builder tests |
| Evaluate | gold dataset | benchmark metrics | evaluation tests |
