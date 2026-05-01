from ingestion.clone import RepoCloner
from ingestion.parser import CodeParser
from ingestion.graph import Neo4jHandler
from ingestion.vector import VectorDBHandler
import logging
import os

logger = logging.getLogger(__name__)

class IngestionPipeline:
    def __init__(self):
        self.graph_handler = Neo4jHandler()
        self.vector_handler = VectorDBHandler()

    def run(self, repo_url: str, temp_dir: str = None):
        logger.info(f"Starting ingestion for {repo_url}")

        # 1. Clone
        cloner = RepoCloner(repo_url, temp_dir=temp_dir)
        repo_path = cloner.clone_repo()
        logger.info(f"Repo cloned to {repo_path}")

        # 2. Parse (Tree-sitter)
        parser = CodeParser()
        all_payloads = []
        for root, _, files in os.walk(repo_path):
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    payloads = parser.parse_file(file_path)
                    all_payloads.extend(payloads)

        logger.info(f"Parsed {len(all_payloads)} functions/classes")

        # 3. Prepare nodes and edges for graph/vector ingestion
        nodes = []
        edges = []
        for payload in all_payloads:
            # Node for function
            node = type('CodeNode', (), {})()
            node.type = "function"
            node.name = payload["name"]
            node.path = payload["filepath"]
            node.content = payload["raw_code"]
            node.start_line = payload.get("start_line")
            node.end_line = payload.get("end_line")
            node.parent = None
            node.dependencies = payload.get("calls", [])

            # Extract docstring and comments (simple heuristics)
            # Docstring: first string literal in the function body
            lines = payload["raw_code"].splitlines()
            docstring = None
            if len(lines) > 1 and (lines[1].strip().startswith('"""') or lines[1].strip().startswith("''")):
                docstring = lines[1].strip()
                # If multi-line docstring, join until closing
                if not (docstring.endswith('"""') or docstring.endswith("''")):
                    for l in lines[2:]:
                        docstring += '\n' + l
                        if l.strip().endswith('"""') or l.strip().endswith("'''"):
                            break
            node.docstring = docstring

            # Comments: collect lines starting with #
            comments = [l.strip() for l in lines if l.strip().startswith('#')]
            node.comments = comments

            nodes.append(node)
            # Edges for calls
            for callee in payload.get("calls", []):
                # Edge: function calls function (by name, not full id)
                edges.append(type('CodeEdge', (), {})())
                edges[-1].source = payload["node_id"]
                edges[-1].target = callee
                edges[-1].type = "calls"

        # Compose ParsedRepo-like object
        parsed_repo = type('ParsedRepo', (), {})()
        parsed_repo.nodes = nodes
        parsed_repo.edges = edges

        # 4. Graph Ingestion
        try:
            self.graph_handler.ingest(parsed_repo)
            logger.info("Graph ingestion completed")
        except Exception as e:
            logger.error(f"Graph ingestion failed: {e}")

        # 5. Vector Ingestion
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
