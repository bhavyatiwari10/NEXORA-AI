Write-Host '=== NEXORA AI ===' -ForegroundColor Magenta
Write-Host 'Terminal 1: backend' -ForegroundColor Cyan
Write-Host '  cd backend; .\.venv\Scripts\Activate.ps1; uvicorn app.main:app --reload --port 8000'
Write-Host ''
Write-Host 'Terminal 2: frontend' -ForegroundColor Cyan
Write-Host '  cd frontend; npm install; npm run dev'
Write-Host ''
Write-Host 'Swagger: http://127.0.0.1:8000/docs'
Write-Host 'Dashboard: http://localhost:5173'
