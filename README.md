# KI für Lehre - RAG System für Vorlesungsunterlagen

Ein vollständiges Retrieval-Augmented Generation (RAG) System, das PDF-Vorlesungsunterlagen in eine durchsuchbare Wissensbasis konvertiert und über einen intelligenten Chat-Assistenten zugänglich macht.

## 🎯 Überblick

Dieses System besteht aus zwei Hauptkomponenten:

1. **PDF zu Markdown Konverter**: Wandelt Ihre PDF-Dokumente in strukturierte Markdown-Dateien um
2. **RAG Terminal Chat**: Nutzt die konvertierten Dokumente als Wissensbasis für einen KI-Assistenten

### Workflow
```
PDF-Dateien → Markdown-Konvertierung → Vektor-Index → Chat-Interface
    (data/)        (llm_ready/)         (storage/)      (Terminal)
```

## 🚀 Schnellstart

```bash
# 1. Umgebung vorbereiten
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 2. Abhängigkeiten installieren
pip install -r requirements.txt

# 3. Ollama installieren und starten
# Download: https://ollama.ai/download
ollama serve

# 4. Benötigte Modelle herunterladen
ollama pull gemma3:27b
ollama pull nomic-embed-text

# 5. PDFs konvertieren
python convert_pdf.py

# 6. RAG Chat starten
python rag_terminal_chat.py
```

## 📋 Systemanforderungen

- **Python**: 3.8 oder höher
- **RAM**: 
  - Mindestens 8 GB (für kleine Modelle)
  - 16+ GB empfohlen (für optimale Qualität mit gemma3:27b)
- **Speicherplatz**: 
  - ~4 GB für marker-pdf Modelle
  - ~16 GB für gemma3:27b
  - ~274 MB für nomic-embed-text
- **GPU**: Optional, aber empfohlen für schnellere Verarbeitung

## 📦 Installation im Detail

### 1. Python-Umgebung

```bash
# Virtuelle Umgebung erstellen
python -m venv venv

# Aktivieren
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

### 2. Abhängigkeiten

```bash
# Alle Pakete installieren
pip install -r requirements.txt

# Wichtige Pakete:
# - marker-pdf==1.7.3 (PDF-Konvertierung)
# - llama-index>=0.12.0 (RAG-Framework)
# - ollama (LLM-Integration)
```

### 3. Ollama Setup

1. Ollama von https://ollama.ai/download herunterladen und installieren
2. Ollama-Service starten:
   ```bash
   ollama serve
   ```
3. Modelle installieren:
   ```bash
   # Hauptmodell (beste Qualität, 16GB RAM)
   ollama pull gemma3:27b
   
   # Embedding-Modell (erforderlich)
   ollama pull nomic-embed-text
   
   # Alternative Modelle (weniger RAM):
   ollama pull gemma2:9b    # ~5.5GB RAM
   ollama pull gemma2:2b    # ~1.5GB RAM
   ```

## 📁 Ordnerstruktur

```
KI für Lehre/
├── data/                    # Eingabe: PDF-Dateien
│   └── *.pdf
├── llm_ready/              # Konvertierte Markdown-Dateien
│   ├── *.md
│   └── *_images/           # Extrahierte Bilder
├── storage/                # Vektor-Index (automatisch erstellt)
├── convert_pdf.py          # PDF-Konvertierungsskript
├── rag_terminal_chat.py    # Chat-Anwendung
├── rag_config.py          # Konfigurationsdatei
├── requirements.txt        # Python-Abhängigkeiten
└── README.md              # Diese Datei
```

## 🔄 Schritt 1: PDF-Konvertierung

### Verwendung

1. **PDFs vorbereiten**: Alle PDF-Dateien in den `data/` Ordner legen

2. **Konvertierung starten**:
   ```bash
   python convert_pdf.py
   ```

3. **Ergebnisse**: Markdown-Dateien werden im `llm_ready/` Ordner erstellt

### Features

- ✅ Batch-Verarbeitung aller PDFs
- ✅ Erhält Dateinamen (nur .pdf → .md)
- ✅ Extrahiert eingebettete Bilder
- ✅ Unterstützt komplexe Layouts und mathematische Formeln
- ✅ Fortschrittsanzeige während der Konvertierung

### Erweiterte Optionen

```bash
# OCR für alle Seiten erzwingen
OCR_ALL_PAGES=true python convert_pdf.py

# CPU statt GPU verwenden
TORCH_DEVICE=cpu python convert_pdf.py
```

## 💬 Schritt 2: RAG Chat verwenden

### Grundlegende Nutzung

```bash
# Standard starten (gemma3:27b)
python rag_terminal_chat.py

# Mit alternativem Modell
python rag_terminal_chat.py --model gemma2:9b

# Index neu erstellen
python rag_terminal_chat.py --rebuild
```

### Chat-Befehle

- `/help` - Zeigt Hilfe und Tipps
- `/models` - Zeigt verfügbare Modelle
- `/clear` - Löscht den Chat-Verlauf
- `/rebuild` - Erstellt den Index neu
- `/exit` - Beendet das Programm

### Beispiel-Interaktion

```
👤 Du: Was ist Initialisierung in der Programmierung?
🤖 Assistent: Initialisierung bezeichnet den Vorgang, bei dem einer Variablen 
             ein Anfangswert zugewiesen wird...

👤 Du: Gib mir ein Beispiel für Array-Initialisierung
🤖 Assistent: Hier sind einige Beispiele für Array-Initialisierung:
             int[] zahlen = {1, 2, 3, 4, 5};
             String[] namen = new String[10];
             ...
```

## ⚙️ Konfiguration

Bearbeiten Sie `rag_config.py` für erweiterte Einstellungen:

### Modellauswahl

```python
DEFAULT_CONFIG = {
    "llm_model": "gemma3:27b",  # Standard für beste Qualität
    "embedding_model": "nomic-embed-text",
    "chunk_size": 512,
    "chunk_overlap": 50,
    "temperature": 0.7,
    ...üüp
}
```

### Verfügbare Modelle

| Modell | RAM | Geschwindigkeit | Qualität | Verwendung |
|--------|-----|-----------------|----------|------------|
| gemma2:2b | 4GB | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | Schnelle Tests |
| gemma2:9b | 8GB | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Ausgewogen |
| gemma3:27b | 16GB+ | ⭐⭐ | ⭐⭐⭐⭐⭐ | Beste Qualität |

## 🏗️ Technische Architektur

```
PDF-Konvertierung (marker-pdf)
├── PDF Parser
├── Layout-Analyse
├── OCR (bei Bedarf)
└── Markdown-Generator

RAG-System (LlamaIndex)
├── Dokument-Loader
├── Text-Splitter (Chunks)
├── Embedding-Generator (nomic-embed-text)
├── Vektor-Index
├── Retriever (Top-K Similarity)
├── LLM (Ollama)
└── Chat-Memory
```

## 🐛 Fehlerbehebung

### PDF-Konvertierung

**Problem**: "marker-pdf ist nicht installiert!"
```bash
pip install --upgrade marker-pdf==1.7.3
```

**Problem**: Speicherfehler bei großen PDFs
- Verarbeiten Sie große PDFs einzeln
- Nutzen Sie `TORCH_DEVICE=cpu` für weniger RAM-Verbrauch

### RAG Chat

**Problem**: "Ollama Verbindung fehlgeschlagen"
```bash
# Ollama starten
ollama serve

# Verbindung testen
curl http://localhost:11434/api/tags
```

**Problem**: "Modell nicht gefunden"
```bash
# Modelle installieren
ollama pull gemma3:27b
ollama pull nomic-embed-text
```

**Problem**: Speicherfehler mit gemma3:27b
```bash
# Kleineres Modell verwenden
python rag_terminal_chat.py --model gemma2:9b
```

## 📊 Performance-Optimierung

### 1. Erste Ausführung
- PDF-Konvertierung: ~1-5 Minuten pro PDF
- Index-Erstellung: ~1-5 Minuten (einmalig)
- Modell-Download: ~10-30 Minuten (einmalig)

### 2. Folgende Nutzung
- Chat-Start: ~10-30 Sekunden
- Antwortzeit: ~2-10 Sekunden (je nach Modell)

### 3. Tipps
- Index wird gecacht in `./storage`
- Nutzen Sie `/rebuild` nur bei neuen Dokumenten
- Kleinere Chunk-Größen für präzisere Antworten
- Größere Chunks für mehr Kontext

## 🔧 Erweiterte Funktionen

### Batch-Verarbeitung von Fragen

```python
from rag_terminal_chat import RAGTerminalChat

# System initialisieren
rag = RAGTerminalChat()
rag.build_index()
rag.setup_chat_engine()

# Mehrere Fragen verarbeiten
fragen = [
    "Was ist Objektorientierung?",
    "Erkläre Vererbung",
    "Beispiel für Polymorphismus"
]

for frage in fragen:
    antwort = rag.chat_engine.chat(frage)
    print(f"F: {frage}\nA: {antwort}\n{'-'*50}\n")
```

### Eigene Modelle verwenden

1. Modell installieren:
   ```bash
   ollama pull ihr-modell:tag
   ```

2. In Konfiguration eintragen oder per CLI:
   ```bash
   python rag_terminal_chat.py --model ihr-modell:tag
   ```

## 📚 Weitere Ressourcen

- [Ollama Dokumentation](https://github.com/ollama/ollama)
- [LlamaIndex Dokumentation](https://docs.llamaindex.ai/)
- [marker-pdf Repository](https://github.com/VikParuchuri/marker)
- [RAG Konzepte erklärt](https://www.pinecone.io/learn/retrieval-augmented-generation/)

## 🤝 Support

Bei Problemen prüfen Sie bitte:

- [ ] Python-Version (3.11+)
- [ ] Alle Abhängigkeiten installiert (`pip list`)
- [ ] Ollama läuft (`ollama serve`)
- [ ] Modelle installiert (`ollama list`)
- [ ] PDF-Dateien im `data/` Ordner
- [ ] Konvertierte Dateien im `llm_ready/` Ordner
- [ ] Ausreichend RAM verfügbar

---

Viel Erfolg beim Lernen mit Ihrem persönlichen KI-Assistenten! 🎓🤖 