import ast
import os
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class CodeNode(BaseModel):
    type: str  # "file", "class", "function"
    name: str
    path: str
    content: Optional[str] = None
    start_line: Optional[int] = None
    end_line: Optional[int] = None
    parent: Optional[str] = None # Name of parent node

class CodeEdge(BaseModel):
    source: str
    target: str
    type: str # "calls", "imports", "defines"

class ParsedRepo(BaseModel):
    nodes: List[CodeNode]
    edges: List[CodeEdge]

class PythonASTParser:
    def __init__(self, repo_path: str):
        self.repo_path = repo_path
        self.nodes = []
        self.edges = []

    def parse(self) -> ParsedRepo:
        for root, _, files in os.walk(self.repo_path):
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    self._parse_file(file_path)
        return ParsedRepo(nodes=self.nodes, edges=self.edges)

    def _parse_file(self, file_path: str):
        rel_path = os.path.relpath(file_path, self.repo_path)
        
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            lines = content.splitlines()
        
        # File Node
        file_node = CodeNode(
            type="file",
            name=rel_path,
            path=rel_path,
            content=content
        )
        self.nodes.append(file_node)

        try:
            tree = ast.parse(content)
        except SyntaxError:
            return # Skip files with syntax errors

        # Walk the AST
        self._visit_node(tree, rel_path, rel_path, lines)

    def _visit_node(self, node, file_path, parent_name, lines):
        for child in ast.iter_fields(node):
            child = child[1] if isinstance(child, tuple) else child
            if isinstance(child, list):
                for item in child:
                    if isinstance(item, ast.AST):
                        self._process_ast_item(item, file_path, parent_name, lines)
            elif isinstance(child, ast.AST):
                self._process_ast_item(child, file_path, parent_name, lines)

    def _process_ast_item(self, item, file_path, parent_name, lines):
        if isinstance(item, ast.ClassDef):
            class_name = item.name
            full_name = f"{file_path}::{class_name}"
            
            # Extract content
            start = item.lineno - 1
            end = item.end_lineno
            node_content = "\n".join(lines[start:end])

            # Class Node
            self.nodes.append(CodeNode(
                type="class",
                name=class_name,
                path=file_path,
                start_line=item.lineno,
                end_line=item.end_lineno,
                parent=parent_name,
                content=node_content
            ))
            
            # Edge: Parent defines Class
            self.edges.append(CodeEdge(source=parent_name, target=full_name, type="defines"))
            
            # Recurse
            self._visit_node(item, file_path, full_name, lines)

        elif isinstance(item, ast.FunctionDef) or isinstance(item, ast.AsyncFunctionDef):
            func_name = item.name
            full_name = f"{parent_name}::{func_name}"
            
            # Extract content
            start = item.lineno - 1
            end = item.end_lineno
            node_content = "\n".join(lines[start:end])

            # Function Node
            self.nodes.append(CodeNode(
                type="function",
                name=func_name,
                path=file_path,
                start_line=item.lineno,
                end_line=item.end_lineno,
                parent=parent_name,
                content=node_content
            ))
            
            # Edge: Parent defines Function
            self.edges.append(CodeEdge(source=parent_name, target=full_name, type="defines"))
            
            # Check for calls inside function
            self._find_calls(item, full_name)

        elif isinstance(item, ast.Import) or isinstance(item, ast.ImportFrom):
            # Handle imports (simplified)
            pass

    def _find_calls(self, node, caller_name):
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name):
                    called_name = child.func.id
                    # Edge: Function calls Function (This is weak linking, just by name)
                    self.edges.append(CodeEdge(source=caller_name, target=called_name, type="calls"))
                elif isinstance(child.func, ast.Attribute):
                    # Handle obj.method() calls - simplified
                    pass
