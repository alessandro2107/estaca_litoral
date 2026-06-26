# Ativa o ambiente virtual do projeto e inicia o Streamlit
# Uso: execute este script no PowerShell dentro da pasta do projeto

$venvPath = Join-Path $PSScriptRoot ".venv\Scripts\Activate.ps1"
if (-Not (Test-Path $venvPath)) {
    Write-Error "Ambiente virtual não encontrado em: $venvPath"
    exit 1
}

Write-Host "Ativando ambiente virtual..." -ForegroundColor Green
. $venvPath

Write-Host "Iniciando o Streamlit..." -ForegroundColor Green
python -m streamlit run app.py
