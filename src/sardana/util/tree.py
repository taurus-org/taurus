class BaseNode:
    """BaseNode, stores reference to data."""
    
    def __init__(self, data):
        self.data = data

class BranchNode(BaseNode):
    """BranchNode, apart of reference to data, stores a list of 
    children Nodes."""
    def __init__(self, data):
        BaseNode.__init__(self, data)
        self.children = []

    def addChild(self, child):
        self.children.append(child)

class LeafNode(BaseNode):
    """LeafMode, just stores reference to data."""
    def __init__(self, data):
        BaseNode.__init__(self, data)

class Tree:
    """Base tree class, stores reference to root Node object"""
    def __init__(self, root):
        self._root = root
        
    def root(self):
        return self._root