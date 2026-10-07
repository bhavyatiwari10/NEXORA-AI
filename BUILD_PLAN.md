# Nexora Build Plan

## Folder tree
```text
nexora/
├── backend/
│   ├── app/
│   │   ├── api/             # versioned REST endpoints
│   │   ├── core/            # config, DB, security, errors
│   │   ├── models/          # SQLAlchemy entities
│   │   ├── schemas/         # Pydantic v2 DTOs
│   │   ├── services/        # domain services
│   │   ├── llm/             # provider abstraction + mock/OpenAI/Anthropic
│   │   ├── pipeline/        # ingestion → extraction → validation → order
│   │   ├── scheduler/       # APScheduler follow-ups
│   │   └── evaluation/      # benchmark + metrics
│   └── tests/
├── frontend/
│   └── src/
│       ├── components/
│       ├── pages/
│       ├── services/
│       ├── charts/
│       ├── utils/
│       └── tests/
├── data/                    # seed + gold dataset
├── docs/
├── docker-compose.yml
├── Makefile
└── .env.example
```

## Build order
1. Backend foundation: config, database, models, schemas, auth, error handling.
2. Chat ingestion + deterministic MockLLM + extraction validation.
3. Pipeline tracker + customer/product resolution + order creation.
4. GST invoices, payment simulation, PDF generation.
5. Follow-ups + scheduler + reminder drafts.
6. Analytics + safe Ask Nexora query specification.
7. Evaluation framework + gold dataset + metrics.
8. React dashboard and all primary pages.
9. Tests, Docker, seed/demo mode, docs, accessibility and polish.

## Sensible defaults
- SQLite is the default development database; `DATABASE_URL` can point to PostgreSQL.
- `LLM_PROVIDER=mock` makes the full application work offline without API keys.
- Demo authentication uses a seeded admin account and JWT.
- Seller state defaults to Uttar Pradesh for GST simulation and can be changed in Settings.
- Payment links are intentionally simulated and never connect to a real payment processor.
