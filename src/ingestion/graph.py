from neo4j import GraphDatabase
from app.core.config import settings
from app.ingestion.parser import ParsedRepo
import logging

logger = logging.getLogger(__name__)

class Neo4jHandler:
    def __init__(self):
        self.driver = None
        try:
            self.driver = GraphDatabase.driver(
                settings.NEO4J_URI, 
                auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
            )
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {e}")

    def close(self):
        if self.driver:
            self.driver.close()

    def clear_database(self):
        if not self.driver: return
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")

    def ingest(self, parsed_repo: ParsedRepo):
        if not self.driver:
            logger.warning("Neo4j driver not initialized. Skipping graph ingestion.")
            return

        with self.driver.session() as session:
            # Create Nodes
            for node in parsed_repo.nodes:
                if node.type == "file":
                    session.run(
                        "MERGE (f:File {path: $path, name: $name})",
                        path=node.path, name=node.name
                    )
                elif node.type == "class":
                    session.run(
                        "MERGE (c:Class {name: $name, path: $path})",
                        name=node.name, path=node.path
                    )
                elif node.type == "function":
                    session.run(
                        "MERGE (f:Function {name: $name, path: $path})",
                        name=node.name, path=node.path
                    )

            # Create Edges
            for edge in parsed_repo.edges:
                if edge.type == "defines":
                    # This is a bit simplified. We need to match nodes correctly.
                    # Assuming source is parent name/path and target is child full name
                    # But my parser logic for names was a bit mixed. 
                    # Let's rely on the fact that we can match by name for now, 
                    # but in production we need unique IDs (filepath + name).
                    pass 
                    # TODO: Improve edge creation logic based on unique identifiers
                    
                # For now, let's just log that we would create edges
                # session.run(...)
