#!/usr/bin/env python3
"""
RAG Terminal Chat mit Ollama und LlamaIndex

Dieses Skript erstellt ein RAG-System, das die Markdown-Dateien aus dem
'llm_ready' Ordner als Wissensbasis nutzt und über Ollama mit konfigurierbaren
Modellen interagiert.
"""

import os
import sys
from pathlib import Path
from typing import List, Optional
import logging

# LlamaIndex Imports
try:
    from llama_index.core import (
        VectorStoreIndex,
        SimpleDirectoryReader,
        Settings,
        StorageContext,
        load_index_from_storage
    )
    from llama_index.core.node_parser import SentenceSplitter
    from llama_index.llms.ollama import Ollama
    from llama_index.embeddings.ollama import OllamaEmbedding
    from llama_index.core.memory import Memory
    # Optionale erweiterte Memory-Features
    try:
        from llama_index.core.memory import FactExtractionMemoryBlock
        ADVANCED_MEMORY_AVAILABLE = True
    except ImportError:
        ADVANCED_MEMORY_AVAILABLE = False
except ImportError as e:
    print(f"❌ Fehler beim Import von LlamaIndex: {e}")
    print("\nBitte installieren Sie die benötigten Pakete:")
    print("pip install llama-index llama-index-llms-ollama llama-index-embeddings-ollama")
    sys.exit(1)

# Konfiguration importieren
try:
    from rag_config import DEFAULT_CONFIG, ADVANCED_CONFIG, AVAILABLE_MODELS, EMBEDDING_MODELS
except ImportError:
    print("⚠️ Konfigurationsdatei nicht gefunden, verwende Standardwerte")
    DEFAULT_CONFIG = {
        "llm_model": "gemma3:27b",
        "embedding_model": "nomic-embed-text",
        "data_dir": "./llm_ready",
        "index_dir": "./storage",
        "chunk_size": 512,
        "chunk_overlap": 50,
        "temperature": 0.7,
        "request_timeout": 120.0,
        "memory_token_limit": 3000,
        "system_prompt": """Du bist ein hilfreicher Assistent, der Fragen zu den Vorlesungsunterlagen beantwortet.
Nutze die bereitgestellten Informationen aus den Dokumenten, um präzise und hilfreiche Antworten zu geben.
Wenn du dir bei einer Antwort nicht sicher bist, sage das ehrlich.
Antworte immer auf Deutsch."""
    }
    ADVANCED_CONFIG = {
        "ollama_base_url": "http://localhost:11434",
        "log_level": "INFO"
    }
    AVAILABLE_MODELS = {}
    EMBEDDING_MODELS = {}

# Logging konfigurieren
log_level = getattr(logging, ADVANCED_CONFIG.get("log_level", "INFO"))
logging.basicConfig(level=log_level)
logger = logging.getLogger(__name__)


class RAGTerminalChat:
    """Terminal-basiertes RAG Chat System mit Ollama."""
    
    def __init__(self, config: dict = None):
        """
        Initialisiert das RAG System.
        
        Args:
            config: Konfigurationsdictionary (optional, nutzt DEFAULT_CONFIG wenn None)
        """
        self.config = config or DEFAULT_CONFIG
        self.data_dir = Path(self.config["data_dir"])
        self.index_dir = Path(self.config["index_dir"])
        self.model_name = self.config["llm_model"]
        self.embedding_model = self.config["embedding_model"]
        self.index = None
        self.chat_engine = None
        
        # Überprüfe ob Datenverzeichnis existiert
        if not self.data_dir.exists():
            raise FileNotFoundError(f"Datenverzeichnis '{self.data_dir}' nicht gefunden!")
        
        # Initialisiere Ollama
        self._setup_ollama()
        
    def _setup_ollama(self):
        """Konfiguriert Ollama LLM und Embeddings."""
        print(f"🤖 Initialisiere Ollama mit Modell: {self.model_name}")
        
        # LLM Setup
        self.llm = Ollama(
            model=self.model_name,
            request_timeout=self.config["request_timeout"],
            temperature=self.config["temperature"],
            base_url=ADVANCED_CONFIG.get("ollama_base_url", "http://localhost:11434")
        )
        
        # Embedding Setup
        self.embed_model = OllamaEmbedding(
            model_name=self.embedding_model,
            base_url=ADVANCED_CONFIG.get("ollama_base_url", "http://localhost:11434")
        )
        
        # Text Splitter für Chunking (neu: bevorzugte Methode)
        self.text_splitter = SentenceSplitter(
            chunk_size=self.config["chunk_size"],
            chunk_overlap=self.config["chunk_overlap"]
        )
        
        # Globale Settings
        Settings.llm = self.llm
        Settings.embed_model = self.embed_model
        Settings.text_splitter = self.text_splitter  # Neu: Verwende text_splitter statt chunk_size/overlap
        
        print("✓ Ollama erfolgreich konfiguriert")
        
    def _check_ollama_connection(self) -> bool:
        """Überprüft die Verbindung zu Ollama."""
        try:
            # Teste die Verbindung mit einer einfachen Anfrage
            response = self.llm.complete("Test")
            return True
        except Exception as e:
            print(f"❌ Fehler bei der Verbindung zu Ollama: {e}")
            print("\nStellen Sie sicher, dass:")
            print("1. Ollama läuft (ollama serve)")
            print(f"2. Das Modell '{self.model_name}' installiert ist (ollama pull {self.model_name})")
            print(f"3. Das Embedding-Modell '{self.embedding_model}' installiert ist (ollama pull {self.embedding_model})")
            
            # Zeige verfügbare Modelloptionen
            if AVAILABLE_MODELS:
                print("\n📋 Verfügbare Modellkonfigurationen:")
                for key, model_info in AVAILABLE_MODELS.items():
                    print(f"   - {key}: {model_info['llm']} - {model_info['description']}")
            
            return False
    
    def build_index(self, force_rebuild: bool = False):
        """
        Erstellt oder lädt den Vektorindex.
        
        Args:
            force_rebuild: Erzwingt Neuerstellung des Index
        """
        # Prüfe ob Index bereits existiert
        if self.index_dir.exists() and not force_rebuild:
            print("📂 Lade vorhandenen Index...")
            try:
                storage_context = StorageContext.from_defaults(
                    persist_dir=str(self.index_dir)
                )
                self.index = load_index_from_storage(storage_context)
                print("✓ Index erfolgreich geladen")
                return
            except Exception as e:
                print(f"⚠️ Fehler beim Laden des Index: {e}")
                print("Erstelle neuen Index...")
        
        # Erstelle neuen Index
        print(f"📚 Lade Dokumente aus: {self.data_dir}")
        
        # Lade alle Markdown-Dateien
        documents = SimpleDirectoryReader(
            input_dir=str(self.data_dir),
            recursive=True,
            filename_as_id=True,
            required_exts=[".md"]
        ).load_data()
        
        if not documents:
            raise ValueError(f"Keine Markdown-Dateien in '{self.data_dir}' gefunden!")
        
        print(f"✓ {len(documents)} Dokumente geladen")
        
        # Erstelle Index
        print("🔨 Erstelle Vektorindex...")
        print("  (Dies kann beim ersten Mal einige Minuten dauern)")
        
        # Erstelle Index mit Transformations (neue API)
        self.index = VectorStoreIndex.from_documents(
            documents,
            transformations=[self.text_splitter],  # Neu: transformations statt node_parser
            show_progress=True
        )
        
        # Speichere Index
        print("💾 Speichere Index...")
        self.index.storage_context.persist(persist_dir=str(self.index_dir))
        print("✓ Index erfolgreich erstellt und gespeichert")
    
    def setup_chat_engine(self):
        """Richtet die Chat-Engine mit Memory ein."""
        if not self.index:
            raise ValueError("Index muss zuerst erstellt werden!")
        
        # Prüfe ob erweiterte Memory verwendet werden soll
        use_advanced = ADVANCED_CONFIG.get("use_advanced_memory", False)
        
        if use_advanced and ADVANCED_MEMORY_AVAILABLE:
            # Erweiterte Memory mit Fact Extraction
            print("📊 Verwende erweiterte Memory mit Fact Extraction...")
            memory_blocks = [
                FactExtractionMemoryBlock(
                    name="extracted_facts",
                    llm=self.llm,
                    max_facts=ADVANCED_CONFIG.get("max_facts", 50),
                    priority=1,
                )
            ]
            memory = Memory.from_defaults(
                session_id="chat_history",
                token_limit=self.config["memory_token_limit"],
                memory_blocks=memory_blocks
            )
        else:
            # Einfache Short-Term Memory (Standard)
            if use_advanced and not ADVANCED_MEMORY_AVAILABLE:
                print("⚠️ Erweiterte Memory angefordert, aber nicht verfügbar. Nutze Standard-Memory.")
            
            memory = Memory.from_defaults(
                session_id="chat_history",
                token_limit=self.config["memory_token_limit"]
            )
        
        # Retrieval-Einstellungen aus erweiterten Konfigs
        similarity_top_k = ADVANCED_CONFIG.get("similarity_top_k", 3)
        
        # Erstelle Chat Engine
        self.chat_engine = self.index.as_chat_engine(
            chat_mode="context",
            memory=memory,
            system_prompt=self.config["system_prompt"],
            similarity_top_k=similarity_top_k,
            verbose=True
        )
        
        print("✓ Chat-Engine bereit")
    
    def chat_loop(self):
        """Hauptschleife für die Terminal-Interaktion."""
        print("\n" + "="*60)
        print("🎓 RAG CHAT - Vorlesungsunterlagen Assistent")
        print("="*60)
        print(f"Modell: {self.model_name}")
        print(f"Datenquelle: {self.data_dir}")
        print("\nBefehle:")
        print("  /help    - Zeige diese Hilfe")
        print("  /clear   - Lösche Chat-Verlauf")
        print("  /rebuild - Erstelle Index neu")
        print("  /models  - Zeige verfügbare Modelle")
        print("  /exit    - Beende das Programm")
        print("\nStelle deine Fragen zu den Vorlesungsunterlagen!")
        print("-"*60 + "\n")
        
        while True:
            try:
                # Benutzereingabe
                user_input = input("\n👤 Du: ").strip()
                
                if not user_input:
                    continue
                
                # Befehle verarbeiten
                if user_input.lower() == "/exit":
                    print("\n👋 Auf Wiedersehen!")
                    break
                
                elif user_input.lower() == "/help":
                    self._show_help()
                    continue
                
                elif user_input.lower() == "/models":
                    self._show_models()
                    continue
                
                elif user_input.lower() == "/clear":
                    self.setup_chat_engine()  # Neue Engine = neuer Memory
                    print("✓ Chat-Verlauf gelöscht")
                    continue
                
                elif user_input.lower() == "/rebuild":
                    print("\n🔄 Erstelle Index neu...")
                    self.build_index(force_rebuild=True)
                    self.setup_chat_engine()
                    print("✓ Index wurde neu erstellt")
                    continue
                
                # Verarbeite Anfrage
                print("\n🤖 Assistent: ", end="", flush=True)
                print("(denke nach...)", end="\r", flush=True)
                
                # Sende Anfrage an Chat Engine
                response = self.chat_engine.chat(user_input)
                
                # Lösche "denke nach..." und zeige Antwort
                print(" " * 20, end="\r")  # Überschreibe die Zeile
                print(f"🤖 Assistent: {response}")
                
            except KeyboardInterrupt:
                print("\n\n⚠️ Abbruch durch Benutzer")
                break
            except Exception as e:
                print(f"\n❌ Fehler: {e}")
                print("Versuche es erneut oder beende mit /exit")
    
    def _show_help(self):
        """Zeigt die Hilfe an."""
        print("\n📖 HILFE")
        print("-"*40)
        print("Dieses System nutzt RAG (Retrieval-Augmented Generation),")
        print("um Fragen zu den Vorlesungsunterlagen zu beantworten.")
        print("\nTipps für bessere Antworten:")
        print("- Stelle spezifische Fragen")
        print("- Nenne Themen oder Kapitel, wenn bekannt")
        print("- Frage nach Erklärungen oder Beispielen")
        print("\nBeispiele:")
        print("- 'Was ist Initialisierung in der Programmierung?'")
        print("- 'Erkläre mir Arrays'")
        print("- 'Welche Themen werden in der Vorlesung behandelt?'")
        print("-"*40)
    
    def _show_models(self):
        """Zeigt verfügbare Modelle an."""
        print("\n🤖 VERFÜGBARE MODELLE")
        print("-"*40)
        print(f"Aktuelles LLM: {self.model_name}")
        print(f"Aktuelles Embedding: {self.embedding_model}")
        
        if AVAILABLE_MODELS:
            print("\n📚 LLM-Modelle:")
            for key, model_info in AVAILABLE_MODELS.items():
                status = " (AKTIV)" if model_info['llm'] == self.model_name else ""
                print(f"  {key}: {model_info['llm']}{status}")
                print(f"    → {model_info['description']}")
        
        if EMBEDDING_MODELS:
            print("\n🔍 Embedding-Modelle:")
            for key, embed_info in EMBEDDING_MODELS.items():
                status = " (AKTIV)" if embed_info['model'] == self.embedding_model else ""
                print(f"  {key}: {embed_info['model']}{status}")
                print(f"    → {embed_info['description']}")
                print(f"    → Größe: {embed_info['size']}")
        
        print("\nUm das Modell zu ändern, bearbeiten Sie rag_config.py")
        print("und starten Sie das Programm neu.")
        print("-"*40)


def main():
    """Hauptfunktion."""
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description="RAG Terminal Chat System")
    parser.add_argument("--model", help="Ollama Modell (überschreibt Konfiguration)")
    parser.add_argument("--rebuild", action="store_true", help="Index neu erstellen")
    args = parser.parse_args()
    
    try:
        # Konfiguration laden und ggf. überschreiben
        config = DEFAULT_CONFIG.copy()
        if args.model:
            config["llm_model"] = args.model
            print(f"📝 Verwende Modell aus Kommandozeile: {args.model}")
        
        # Initialisiere RAG System
        print("🚀 Starte RAG Terminal Chat...")
        
        rag_chat = RAGTerminalChat(config=config)
        
        # Überprüfe Ollama-Verbindung
        print("\n🔍 Überprüfe Ollama-Verbindung...")
        if not rag_chat._check_ollama_connection():
            sys.exit(1)
        
        # Baue oder lade Index
        rag_chat.build_index(force_rebuild=args.rebuild)
        
        # Setup Chat Engine
        rag_chat.setup_chat_engine()
        
        # Starte Chat Loop
        rag_chat.chat_loop()
        
    except FileNotFoundError as e:
        print(f"\n❌ Fehler: {e}")
        print(f"Stelle sicher, dass der Ordner '{config['data_dir']}' existiert")
        print("und Markdown-Dateien enthält.")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n👋 Programm beendet.")
    except Exception as e:
        print(f"\n❌ Unerwarteter Fehler: {e}")
        logger.exception("Unerwarteter Fehler")
        sys.exit(1)


if __name__ == "__main__":
    main() 