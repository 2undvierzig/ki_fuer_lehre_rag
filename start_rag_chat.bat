@echo off
echo ==========================================
echo RAG CHAT SYSTEM STARTER
echo ==========================================
echo.

REM Prüfe ob Python verfügbar ist
python --version >nul 2>&1
if errorlevel 1 (
    echo [FEHLER] Python ist nicht installiert oder nicht im PATH!
    echo Bitte installieren Sie Python 3.8 oder höher.
    pause
    exit /b 1
)

REM Prüfe ob Ollama läuft
echo [1/4] Pruefe Ollama-Status...
curl -s http://localhost:11434/api/tags >nul 2>&1
if errorlevel 1 (
    echo Ollama laeuft nicht. Starte Ollama...
    start /B ollama serve
    echo Warte 5 Sekunden auf Ollama-Start...
    timeout /t 5 /nobreak >nul
) else (
    echo Ollama laeuft bereits.
)

REM Prüfe ob benötigte Modelle installiert sind
echo.
echo [2/4] Pruefe installierte Modelle...
ollama list | findstr /i "gemma3:27b" >nul 2>&1
if errorlevel 1 (
    echo gemma3:27b nicht gefunden. Lade Modell herunter...
    echo Dies kann einige Minuten dauern (ca. 16GB)...
    ollama pull gemma3:27b
) else (
    echo gemma3:27b ist installiert.
)

ollama list | findstr /i "nomic-embed-text" >nul 2>&1
if errorlevel 1 (
    echo nomic-embed-text nicht gefunden. Lade Modell herunter...
    ollama pull nomic-embed-text
) else (
    echo nomic-embed-text ist installiert.
)

REM Prüfe ob llm_ready Ordner existiert
echo.
echo [3/4] Pruefe Datenordner...
if not exist "llm_ready" (
    echo [WARNUNG] Ordner 'llm_ready' nicht gefunden!
    echo Bitte zuerst PDFs mit convert_pdf.py konvertieren.
    pause
    exit /b 1
)

REM Zähle Markdown-Dateien
for /f %%A in ('dir /b "llm_ready\*.md" 2^>nul ^| find /c /v ""') do set MD_COUNT=%%A
if "%MD_COUNT%"=="0" (
    echo [WARNUNG] Keine Markdown-Dateien in llm_ready gefunden!
    echo Bitte zuerst PDFs mit convert_pdf.py konvertieren.
    pause
    exit /b 1
) else (
    echo %MD_COUNT% Markdown-Datei(en) gefunden.
)

REM Starte RAG Chat
echo.
echo [4/4] Starte RAG Chat System...
echo ==========================================
echo.

REM Optionen für verschiedene Modelle
echo Waehlen Sie ein Modell:
echo [1] gemma3:27b (Standard - Beste Qualitaet, ~16GB RAM)
echo [2] gemma2:9b (Mittel - Gute Balance, ~8GB RAM)
echo [3] gemma2:2b (Klein - Schnell, ~4GB RAM)
echo [4] Eigenes Modell eingeben
echo.

set /p CHOICE="Ihre Wahl (1-4) [Standard=1]: "

if "%CHOICE%"=="" set CHOICE=1

if "%CHOICE%"=="1" (
    python rag_terminal_chat.py
) else if "%CHOICE%"=="2" (
    echo Pruefe ob gemma2:9b installiert ist...
    ollama list | findstr /i "gemma2:9b" >nul 2>&1
    if errorlevel 1 (
        echo Lade gemma2:9b herunter...
        ollama pull gemma2:9b
    )
    python rag_terminal_chat.py --model gemma2:9b
) else if "%CHOICE%"=="3" (
    echo Pruefe ob gemma2:2b installiert ist...
    ollama list | findstr /i "gemma2:2b" >nul 2>&1
    if errorlevel 1 (
        echo Lade gemma2:2b herunter...
        ollama pull gemma2:2b
    )
    python rag_terminal_chat.py --model gemma2:2b
) else if "%CHOICE%"=="4" (
    set /p MODEL="Modellname eingeben (z.B. mistral:latest): "
    python rag_terminal_chat.py --model %MODEL%
) else (
    echo Ungueltige Auswahl. Verwende Standard...
    python rag_terminal_chat.py
)

echo.
echo ==========================================
echo RAG Chat beendet.
pause 