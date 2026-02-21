
# Tree-sitter based parser for Python code
import os
from tree_sitter import Language, Parser
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
        matches = self.func_query.matches(tree.root_node)
        extracted_functions = []
        for match in matches:
            func_node = match[1].get("function.def")
            name_node = match[1].get("function.name")
            if not func_node or not name_node:
                continue
            func_name = name_node.text.decode('utf8')
            raw_code = func_node.text.decode('utf8')
            node_id = f"{filepath}::function::{func_name}"
            calls = self._extract_calls(func_node)
            payload = {
                "node_id": node_id,
                "name": func_name,
                "filepath": filepath,
                "raw_code": raw_code,
                "calls": list(set(calls))
            }
            extracted_functions.append(payload)
        return extracted_functions

    def _extract_calls(self, node) -> list[str]:
        calls = []
        matches = self.call_query.matches(node)
        for match in matches:
            call_node = match[1].get("call.name")
            if call_node:
                calls.append(call_node.text.decode('utf8'))
        return calls
