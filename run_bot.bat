@echo off
setlocal

cd /d "%~dp0"

echo ========================================
echo   Botersson Windows Launcher
echo ========================================
echo.

where py >nul 2>&1
if errorlevel 1 (
  echo [ERROR] Python launcher "py" nao encontrado.
  echo Instale Python 3.10+ e tente novamente.
  pause
  exit /b 1
)

if not exist "venv\Scripts\python.exe" (
  echo [INFO] Criando ambiente virtual...
  py -m venv venv
  if errorlevel 1 (
    echo [ERROR] Falha ao criar ambiente virtual.
    pause
    exit /b 1
  )
)

echo [INFO] Atualizando pip...
call "venv\Scripts\python.exe" -m pip install --upgrade pip
if errorlevel 1 (
  echo [ERROR] Falha ao atualizar pip.
  pause
  exit /b 1
)

echo [INFO] Instalando dependencias...
call "venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 (
  echo [ERROR] Falha ao instalar dependencias.
  pause
  exit /b 1
)

if not exist ".env" (
  echo [INFO] Criando .env a partir de .env.example...
  copy ".env.example" ".env" >nul
  echo.
  echo [ATENCAO] Configure DISCORD_TOKEN no arquivo .env antes de iniciar.
  echo Arquivo: %cd%\.env
  pause
  exit /b 1
)

where ollama >nul 2>&1
if errorlevel 1 (
  echo [WARN] Ollama nao encontrado no PATH.
  echo Instale o Ollama em https://ollama.com e execute manualmente: ollama serve
) else (
  echo [INFO] Iniciando Ollama em segundo plano...
  start "Botersson Ollama" /min cmd /c "ollama serve"
)

echo.
echo [INFO] Iniciando Botersson...
call "venv\Scripts\python.exe" run.py
set "EXIT_CODE=%ERRORLEVEL%"

echo.
echo [INFO] Botersson finalizado com codigo %EXIT_CODE%.
pause
exit /b %EXIT_CODE%
