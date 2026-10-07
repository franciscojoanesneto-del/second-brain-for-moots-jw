@echo off
chcp 65001 >nul
title Tribunal Walker — FDI Moot Arena (Julia Azevedo Walker)
color 0E

echo ===============================================================================
echo            TRIBUNAL WALKER  ^|  FDI MOOT ARENA ^& SECOND BRAIN
echo                  Oradora Oficial: Julia Azevedo Walker
echo ===============================================================================
echo.

cd /d "%~dp0"

echo [1/3] Verificando dependencias essenciais do Python...
python -m pip install -q -r requirements.txt
if %errorlevel% neq 0 (
    echo [AVISO] Tentando instalar pacotes base individualmente...
    pip install streamlit pandas altair pyyaml google-genai gTTS requests python-dotenv
)

echo [2/3] Validando estrutura do Obsidian Vault...
if not exist "05_Performance_Oral\Rodadas" mkdir "05_Performance_Oral\Rodadas"

echo [3/3] Inicializando Servidor Streamlit da Arena Walker...
echo.
echo ===============================================================================
echo  A plataforma sera aberta automaticamente no seu navegador padrao!
echo  Pressione Ctrl+C nesta janela para encerrar o simulador quando terminar.
echo ===============================================================================
echo.

start "" http://localhost:8501
streamlit run dashboard_walker.py

pause
