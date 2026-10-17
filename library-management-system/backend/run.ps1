# Online Kütüphane — geliştirme sunucusu
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
if (-not (Test-Path ".venv")) {
    py -3.12 -m venv .venv
    .\.venv\Scripts\python.exe -m pip install -r requirements.txt
}
if (-not (Test-Path "library.db")) {
    .\.venv\Scripts\python.exe seed.py
}
.\.venv\Scripts\uvicorn.exe app.main:app --reload --host 127.0.0.1 --port 8000
