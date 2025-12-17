import chromadb
from chromadb.config import Settings as ChromaSettings
from app.core.config import settings
from app.ingestion.parser import ParsedRepo
import logging

logger = logging.getLogger(__name__)

class VectorDBHandler:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=settings.CHROMA_DB_DIR)
        self.collection = self.client.get_or_create_collection(name="code_embeddings")

    def ingest(self, parsed_repo: ParsedRepo):
        documents = []
        metadatas = []
        ids = []

        for node in parsed_repo.nodes:
            if node.type in ["function", "class"] and node.content:
                # Use the extracted content
                documents.append(node.content)
                metadatas.append({
                    "path": node.path, 
                    "type": node.type,
                    "name": node.name,
                    "parent": node.parent or ""
                })
                # Create a unique ID
                unique_id = f"{node.path}::{node.name}::{node.start_line}"
                ids.append(unique_id)
            
            if node.type == "file" and node.content:
                 # Chunking files is better than nothing
                 documents.append(node.content[:2000]) # Simple truncation for now
                 metadatas.append({"path": node.path, "type": "file", "name": node.name})
                 ids.append(node.path)

        if documents:
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            logger.info(f"Ingested {len(documents)} documents into Vector DB.")
