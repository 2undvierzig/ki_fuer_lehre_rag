"""
Konfiguration für das RAG Terminal Chat System

Hier können Sie die Einstellungen für das RAG-System anpassen.
"""

# Verfügbare Ollama Modelle (von klein nach groß)
AVAILABLE_MODELS = {
    "small": {
        "llm": "gemma2:2b",
        "description": "Kleinstes Modell, schnell aber weniger genau (~1.5GB)"
    },
    "medium": {
        "llm": "gemma2:9b", 
        "description": "Mittleres Modell, gute Balance (~5.5GB)"
    },
    "large": {
        "llm": "gemma3:27b",
        "description": "Großes Modell, beste Qualität (~16GB)"
    },
    "alternative": {
        "llm": "llama3.2:latest",
        "description": "Alternative: Meta's Llama 3.2"
    },
    "mistral": {
        "llm": "mistral:latest",
        "description": "Alternative: Mistral 7B"
    }
}

# Verfügbare Embedding-Modelle
EMBEDDING_MODELS = {
    "nomic": {
        "model": "nomic-embed-text",
        "description": "Standard: Hohe Qualität, optimiert für semantische Suche (768 Dimensionen)",
        "size": "~274MB"
    },
    "mxbai": {
        "model": "mxbai-embed-large",
        "description": "Alternative: Größeres Modell, sehr genau (1024 Dimensionen)",
        "size": "~670MB"
    },
    "all-minilm": {
        "model": "all-minilm",
        "description": "Kompakt: Schnell und effizient (384 Dimensionen)",
        "size": "~46MB"
    }
}

# Standard-Konfiguration
DEFAULT_CONFIG = {
    # LLM Modell (kann aus AVAILABLE_MODELS gewählt werden)
    "llm_model": "gemma3:27b",  # Standard: großes Modell für beste Qualität
    
    # Embedding Modell - WICHTIG für RAG!
    # nomic-embed-text bietet beste Balance zwischen Qualität und Geschwindigkeit
    "embedding_model": "nomic-embed-text",
    
    # Verzeichnisse
    "data_dir": "./llm_ready",
    "index_dir": "./storage",
    
    # Chunk-Einstellungen
    "chunk_size": 512,
    "chunk_overlap": 50,
    
    # LLM Einstellungen
    "temperature": 0.7,
    "request_timeout": 120.0,
    
    # Chat Memory
    "memory_token_limit": 3000,
    
    # System Prompt
    "system_prompt": """Du bist ein hilfreicher Assistent, der Fragen zu den Vorlesungsunterlagen beantwortet.
Nutze die bereitgestellten Informationen aus den Dokumenten, um präzise und hilfreiche Antworten zu geben.
Wenn du dir bei einer Antwort nicht sicher bist, sage das ehrlich.
Antworte immer auf Deutsch."""
}

# Erweiterte Einstellungen
ADVANCED_CONFIG = {
    # Retrieval Einstellungen
    "similarity_top_k": 3,  # Anzahl der relevantesten Chunks
    "rerank": True,  # Reranking aktivieren
    
    # Index-Typ (kann erweitert werden)
    "index_type": "vector",  # Optionen: "vector", "keyword", "hybrid"
    
    # Memory-Konfiguration
    "use_advanced_memory": False,  # True für erweiterte Memory mit Fact Extraction
    "max_facts": 50,  # Anzahl der Fakten für erweiterte Memory
    
    # Logging
    "log_level": "INFO",  # DEBUG, INFO, WARNING, ERROR
    
    # Ollama Server
    "ollama_base_url": "http://localhost:11434"
} 