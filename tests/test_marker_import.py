#!/usr/bin/env python3
"""Test-Skript um marker-pdf Import-Probleme zu diagnostizieren"""

import sys
import subprocess

print("=== MARKER-PDF IMPORT TEST (v1.7.x API) ===\n")

# Python Info
print(f"Python Executable: {sys.executable}")
print(f"Python Version: {sys.version}")
print(f"Python Prefix: {sys.prefix}")

# Installierte Pakete prüfen
print("\n=== INSTALLIERTE PAKETE ===")
try:
    result = subprocess.run([sys.executable, "-m", "pip", "list", "|", "findstr", "marker"], 
                          capture_output=True, text=True, shell=True)
    print("marker-bezogene Pakete:")
    print(result.stdout)
except:
    pass

# Import-Tests für neue API
print("\n=== IMPORT TESTS (Neue API v1.7.x) ===")

# Test 1: marker
try:
    import marker
    print("✓ 'import marker' erfolgreich")
    print(f"  Pfad: {marker.__file__}")
    if hasattr(marker, '__version__'):
        print(f"  Version: {marker.__version__}")
except ImportError as e:
    print(f"❌ 'import marker' fehlgeschlagen: {e}")
except Exception as e:
    print(f"❌ Unerwarteter Fehler bei 'import marker': {type(e).__name__}: {e}")

# Test 2: marker.converters.pdf (neue API)
try:
    from marker.converters.pdf import PdfConverter
    print("✓ 'from marker.converters.pdf import PdfConverter' erfolgreich")
except ImportError as e:
    print(f"❌ 'from marker.converters.pdf import PdfConverter' fehlgeschlagen: {e}")
except Exception as e:
    print(f"❌ Unerwarteter Fehler: {type(e).__name__}: {e}")

# Test 3: marker.models.create_model_dict (neue API)
try:
    from marker.models import create_model_dict
    print("✓ 'from marker.models import create_model_dict' erfolgreich")
except ImportError as e:
    print(f"❌ 'from marker.models import create_model_dict' fehlgeschlagen: {e}")
except Exception as e:
    print(f"❌ Unerwarteter Fehler: {type(e).__name__}: {e}")

# Test 4: marker.output (neue API)
try:
    from marker.output import text_from_rendered
    print("✓ 'from marker.output import text_from_rendered' erfolgreich")
except ImportError as e:
    print(f"❌ 'from marker.output import text_from_rendered' fehlgeschlagen: {e}")
except Exception as e:
    print(f"❌ Unerwarteter Fehler: {type(e).__name__}: {e}")

# Test alte API (sollte fehlschlagen bei v1.7.x)
print("\n=== TEST ALTE API (sollte bei v1.7.x fehlschlagen) ===")
try:
    from marker.convert import convert_single_pdf
    print("⚠️  'convert_single_pdf' gefunden - Sie verwenden möglicherweise eine ältere Version")
except ImportError:
    print("✓ Alte API nicht verfügbar (erwartetes Verhalten für v1.7.x)")

try:
    from marker.models import load_all_models
    print("⚠️  'load_all_models' gefunden - Sie verwenden möglicherweise eine ältere Version")
except ImportError:
    print("✓ Alte API nicht verfügbar (erwartetes Verhalten für v1.7.x)")

# Weitere Abhängigkeiten testen
print("\n=== ABHÄNGIGKEITEN TEST ===")
dependencies = ['torch', 'transformers', 'surya', 'pdftext', 'PIL']

for dep in dependencies:
    try:
        __import__(dep)
        print(f"✓ {dep} importierbar")
    except ImportError:
        print(f"❌ {dep} nicht importierbar")
    except Exception as e:
        print(f"⚠️  {dep}: {type(e).__name__}: {e}")

print("\n=== TEST ABGESCHLOSSEN ===")
print("\nFalls Fehler bei der neuen API auftreten:")
print("1. Stellen Sie sicher, dass Sie marker-pdf>=1.7.0 installiert haben")
print("2. pip uninstall marker-pdf")
print("3. pip install marker-pdf==1.7.3")
print("4. Oder für CPU-only: pip install marker-pdf[cpu]==1.7.3") 