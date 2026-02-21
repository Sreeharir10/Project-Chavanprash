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
            for node in parsed_repo.nodes:
                node_id = f"{node.path}::{node.type}::{node.name}"
                props = {
                    "id": node_id,
                    "name": node.name,
                    "filepath": node.path,
                    "type": node.type,
                }
                if node.start_line:
                    props["start_line"] = node.start_line
                if node.end_line:
                    props["end_line"] = node.end_line
                # Upsert node (no raw_code)
                session.run(
                    f"MERGE (n:{node.type.capitalize()} {{id: $id}}) SET n += $props",
                    id=node_id, props=props
                )

            # Edges: expects edge.source and edge.target to be deterministic IDs
            for edge in parsed_repo.edges:
                if edge.type == "calls":
                    session.run(
                        "MERGE (src:Function {id: $src_id}) MERGE (dst:Function {id: $dst_id}) MERGE (src)-[:CALLS]->(dst)",
                        src_id=edge.source, dst_id=edge.target
                    )
                elif edge.type == "defines":
                    session.run(
                        "MERGE (src {id: $src_id}) MERGE (dst {id: $dst_id}) MERGE (src)-[:DEFINES]->(dst)",
                        src_id=edge.source, dst_id=edge.target
                    )
                elif edge.type == "imports":
                    session.run(
                        "MERGE (src:File {id: $src_id}) MERGE (dst:File {id: $dst_id}) MERGE (src)-[:IMPORTS]->(dst)",
                        src_id=edge.source, dst_id=edge.target
                    )
