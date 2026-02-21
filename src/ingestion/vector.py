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
            if node.type in ["function", "class", "model"] and node.content:
                node_id = f"{node.path}::{node.type}::{node.name}"
                # dependencies: expects node.dependencies (list of node_ids) or empty
                dependencies = getattr(node, "dependencies", [])
                if isinstance(dependencies, list):
                    dependencies_str = ",".join(dependencies)
                else:
                    dependencies_str = str(dependencies)
                documents.append(node.content)
                metadatas.append({
                    "node_id": node_id,
                    "name": node.name,
                    "filepath": node.path,
                    "type": node.type,
                    "start_line": node.start_line,
                    "end_line": node.end_line,
                    "dependencies": dependencies_str
                })
                ids.append(node_id)

        if documents:
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            logger.info(f"Ingested {len(documents)} documents into Vector DB.")
