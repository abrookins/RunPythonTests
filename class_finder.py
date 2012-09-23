"""
class_finder.py: Find the class for a given method using the ast module.
"""
import ast


def find_class(filename, method_name):
    """
    Get the name of the enclosing class for `method_name` within `filename`, a
    Python module.
    """
    module = open(filename).read()
    tree = ast.parse(module)
    visitor = ClassFinder(method_name)
    visitor.visit(tree)
    return visitor.parent_class


class ClassFinder(ast.NodeVisitor):
    """
    An `ast.NodeVisitor` subclass that finds the enclosing class object for
    `method_name` and saves it in `self.parent_class`.
    """
    def __init__(self, method_name):
        self.method_name = method_name
        self.parent_class = None

    def visit(self, node,  parent=None):
        """
        Visit a node. Optionally supports passing the parent node `parent`.
        """
        method = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        return visitor(node, parent=parent)

    def visit_FunctionDef(self, node, parent=None):
        """
        Store the name of the enclosing class for `self.method_name` if it
        exists within a class.
        """
        if node.name == self.method_name:
            if parent:
                self.parent_class = parent.name
        super(ClassFinder, self).generic_visit(node)

    def generic_visit(self, node, parent=None):
        """
        Override `NodeVisitor.generic_visit` to pass the parent node into the
        callback for the node we are visiting.
        """
        for field, value in ast.iter_fields(node):
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, ast.AST):
                        self.visit(item, parent=node)
            elif isinstance(value, ast.AST):
                self.visit(value, parent=node)
