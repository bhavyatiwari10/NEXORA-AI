.PHONY: backend frontend test seed
backend:
	cd backend && uvicorn app.main:app --reload --port 8000
frontend:
	cd frontend && npm run dev
test:
	cd backend && python -m pytest -q
seed:
	cd backend && python -m app.seed
