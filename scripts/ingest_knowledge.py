"""Script to ingest knowledge base documents into ChromaDB."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.rag_service import ingest_file

KNOWLEDGE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "knowledge_base")

DOCUMENTS = [
    {"file": "faq.md", "doc_type": "faq", "source": "Veelgestelde Vragen"},
    {"file": "shipping_policy.md", "doc_type": "policy", "source": "Verzendbeleid"},
    {"file": "return_policy.md", "doc_type": "policy", "source": "Retourbeleid"},
]


def main():
    print("Kennisbank documenten laden...")
    total_chunks = 0

    for doc in DOCUMENTS:
        file_path = os.path.join(KNOWLEDGE_DIR, doc["file"])
        if not os.path.exists(file_path):
            print(f"  Overgeslagen: {doc['file']} (niet gevonden)")
            continue

        chunks = ingest_file(file_path, doc["doc_type"], doc["source"])
        print(f"  Geladen: {doc['file']} ({chunks} chunks)")
        total_chunks += chunks

    print(f"\nKlaar! Totaal {total_chunks} chunks geladen in de kennisbank.")


if __name__ == "__main__":
    main()
