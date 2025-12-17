from app.ingestion.clone import RepoCloner
from app.ingestion.parser import PythonASTParser
from app.ingestion.graph import Neo4jHandler
from app.ingestion.vector import VectorDBHandler
import logging

logger = logging.getLogger(__name__)

class IngestionPipeline:
    def __init__(self):
        self.graph_handler = Neo4jHandler()
        self.vector_handler = VectorDBHandler()

    def run(self, repo_url: str):
        logger.info(f"Starting ingestion for {repo_url}")
        
        # 1. Clone
        cloner = RepoCloner(repo_url)
        repo_path = cloner.clone_repo()
        logger.info(f"Repo cloned to {repo_path}")

        # 2. Parse
        parser = PythonASTParser(repo_path)
        parsed_repo = parser.parse()
        logger.info(f"Parsed {len(parsed_repo.nodes)} nodes and {len(parsed_repo.edges)} edges")

        # 3. Graph Ingestion
        try:
            self.graph_handler.ingest(parsed_repo)
            logger.info("Graph ingestion completed")
        except Exception as e:
            logger.error(f"Graph ingestion failed: {e}")

        # 4. Vector Ingestion
        try:
            self.vector_handler.ingest(parsed_repo)
            logger.info("Vector ingestion completed")
        except Exception as e:
            logger.error(f"Vector ingestion failed: {e}")

        return {
            "status": "success",
            "nodes": len(parsed_repo.nodes),
            "edges": len(parsed_repo.edges),
            "repo_path": repo_path
        }
