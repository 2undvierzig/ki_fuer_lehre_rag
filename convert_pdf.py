#!/usr/bin/env python3
"""
PDF zu Markdown Konverter mit marker-pdf

Dieses Skript konvertiert alle PDFs aus dem 'data' Ordner zu Markdown
und speichert sie im 'llm_ready' Ordner.
"""

import os
import sys
from pathlib import Path
from typing import List, Tuple, Dict, Any
from io import BytesIO
from PIL import Image

# Import der neuen marker-pdf 1.7.x API
try:
    from marker.converters.pdf import PdfConverter
    from marker.models import create_model_dict
    from marker.output import text_from_rendered
except ImportError as e:
    print(f"\n❌ Fehler: marker-pdf konnte nicht importiert werden!")
    print(f"Details: {e}")
    print("\nMögliche Lösungen:")
    print("1. Stellen Sie sicher, dass Sie marker-pdf 1.7.x installiert haben")
    print("2. Versuchen Sie: pip install --upgrade marker-pdf==1.7.3")
    print("3. Oder installieren Sie mit: pip install marker-pdf[cpu] für CPU-only")
    print("\nFalls das Problem weiterhin besteht, versuchen Sie:")
    print("  pip uninstall marker-pdf")
    print("  pip install marker-pdf==1.7.3")
    sys.exit(1)


def ensure_output_directory(output_dir: Path) -> None:
    """Erstellt den Ausgabeordner, falls er nicht existiert."""
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"✓ Ausgabeordner '{output_dir}' ist bereit")


def find_pdf_files(input_dir: Path) -> List[Path]:
    """Findet alle PDF-Dateien im angegebenen Verzeichnis."""
    pdf_files = list(input_dir.glob("*.pdf"))
    pdf_files.extend(list(input_dir.glob("*.PDF")))  # Auch Großschreibung
    return sorted(set(pdf_files))  # Duplikate entfernen und sortieren


def convert_pdf_to_markdown(
    pdf_path: Path, 
    converter: PdfConverter,
    output_dir: Path
) -> Tuple[bool, str]:
    """
    Konvertiert eine einzelne PDF zu Markdown mit der neuen marker-pdf API.
    
    Returns:
        Tuple[bool, str]: (Erfolg, Fehlermeldung/Erfolgsmeldung)
    """
    try:
        print(f"\n📄 Verarbeite: {pdf_path.name}")
        
        # PDF konvertieren mit neuer API
        rendered = converter(str(pdf_path))
        
        # Text und Bilder extrahieren
        markdown_text, _, images = text_from_rendered(rendered)
        
        # Ausgabedateiname (gleicher Name, aber .md statt .pdf)
        output_filename = pdf_path.stem + ".md"
        output_path = output_dir / output_filename
        
        # Markdown speichern
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(markdown_text)
        
        # Bilder speichern (falls vorhanden)
        if images:
            # Erstelle Unterordner für Bilder
            image_dir = output_dir / f"{pdf_path.stem}_images"
            image_dir.mkdir(exist_ok=True)
            
            for img_name, img_data in images.items():
                img_path = image_dir / img_name
                if isinstance(img_data, bytes):
                    with open(img_path, "wb") as f:
                        f.write(img_data)
                elif isinstance(img_data, Image.Image):
                    img_data.save(img_path)  # Format ergibt sich aus Endung
                else:
                    raise TypeError(f"Unsupported image type: {type(img_data)}")
            
            print(f"   ✓ {len(images)} Bilder extrahiert nach: {image_dir}")
        
        # Dateigröße für Info
        file_size_mb = output_path.stat().st_size / (1024 * 1024)
        print(f"   ✓ Markdown gespeichert: {output_filename} ({file_size_mb:.2f} MB)")
        
        return True, f"Erfolgreich konvertiert: {pdf_path.name}"
        
    except Exception as e:
        error_msg = f"Fehler bei {pdf_path.name}: {str(e)}"
        print(f"   ❌ {error_msg}")
        return False, error_msg


def main():
    """Hauptfunktion des Konverters."""
    # Pfade definieren
    workspace_dir = Path.cwd()
    input_dir = workspace_dir / "data"
    output_dir = workspace_dir / "llm_ready"
    
    print("🚀 PDF zu Markdown Konverter gestartet")
    print(f"📁 Eingabeordner: {input_dir}")
    print(f"📁 Ausgabeordner: {output_dir}")
    
    # Überprüfe ob Eingabeordner existiert
    if not input_dir.exists():
        print(f"❌ Fehler: Eingabeordner '{input_dir}' existiert nicht!")
        sys.exit(1)
    
    # Ausgabeordner erstellen
    ensure_output_directory(output_dir)
    
    # PDF-Dateien finden
    pdf_files = find_pdf_files(input_dir)
    
    if not pdf_files:
        print("⚠️  Keine PDF-Dateien im Eingabeordner gefunden!")
        return
    
    print(f"\n📊 Gefundene PDFs: {len(pdf_files)}")
    for pdf in pdf_files:
        print(f"   - {pdf.name}")
    
    # Modelle laden mit neuer API (einmalig für alle Dateien)
    print("\n🤖 Lade marker-pdf Modelle...")
    print("   (Dies kann beim ersten Mal länger dauern)")
    try:
        model_dict = create_model_dict()
        converter = PdfConverter(artifact_dict=model_dict)
        print("   ✓ Modelle erfolgreich geladen")
    except Exception as e:
        print(f"❌ Fehler beim Laden der Modelle: {e}")
        sys.exit(1)
    
    # PDFs konvertieren
    print("\n📝 Starte Konvertierung...")
    erfolge = 0
    fehler = 0
    fehler_details = []
    
    for i, pdf_path in enumerate(pdf_files, 1):
        print(f"\n[{i}/{len(pdf_files)}]", end="")
        erfolg, nachricht = convert_pdf_to_markdown(pdf_path, converter, output_dir)
        
        if erfolg:
            erfolge += 1
        else:
            fehler += 1
            fehler_details.append(nachricht)
    
    # Zusammenfassung
    print("\n" + "="*50)
    print("📊 ZUSAMMENFASSUNG")
    print("="*50)
    print(f"✅ Erfolgreich konvertiert: {erfolge}")
    print(f"❌ Fehler: {fehler}")
    
    if fehler_details:
        print("\nFehlerdetails:")
        for detail in fehler_details:
            print(f"   - {detail}")
    
    print(f"\n✨ Konvertierung abgeschlossen!")
    print(f"   Markdown-Dateien befinden sich in: {output_dir}")


if __name__ == "__main__":
    main() 