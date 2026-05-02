
# Tree-sitter based parser for Python code
import os
from tree_sitter import Language, Parser, QueryCursor
import tree_sitter_python as tspython

class CodeParser:
    def __init__(self):
        self.language = Language(tspython.language())
        self.parser = Parser(self.language)
        # Query for function definitions
        self.func_query = self.language.query("""
            (function_definition
              name: (identifier) @function.name
            ) @function.def
        """)
        # Query for function calls
        self.call_query = self.language.query("""
            (call function: (identifier) @call.name)
            (call function: (attribute attribute: (identifier) @call.name))
        """)

    def parse_file(self, filepath: str) -> list[dict]:
        with open(filepath, "rb") as f:
            source_bytes = f.read()
        tree = self.parser.parse(source_bytes)
        cursor = QueryCursor(self.func_query)
        matches = cursor.matches(tree.root_node)
        extracted_functions = []
        for match in matches:
            captures = match[1]
            func_node = captures.get("function.def")
            name_node = captures.get("function.name")
            if isinstance(func_node, list): func_node = func_node[0]
            if isinstance(name_node, list): name_node = name_node[0]
            if not func_node or not name_node:
                continue
            func_name = name_node.text.decode('utf8')
            raw_code = func_node.text.decode('utf8')
            # Extract start and end line numbers (Tree-sitter uses 0-based rows)
            start_line = func_node.start_point[0] + 1
            end_line = func_node.end_point[0] + 1
            node_id = f"{filepath}::function::{func_name}"
            calls = self._extract_calls(func_node)
            payload = {
                "node_id": node_id,
                "name": func_name,
                "filepath": filepath,
                "raw_code": raw_code,
                "calls": list(set(calls)),
                "start_line": start_line,
                "end_line": end_line
            }
            extracted_functions.append(payload)
        return extracted_functions

    def _extract_calls(self, node) -> list[str]:
        calls = []
        cursor = QueryCursor(self.call_query)
        captures = cursor.captures(node)
        for call_node in captures.get("call.name", []):
            calls.append(call_node.text.decode('utf8'))
        return calls