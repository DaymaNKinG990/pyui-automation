import pytest
from unittest.mock import MagicMock, patch
from pyui_automation.elements.tree import TreeView, TreeNode


@pytest.fixture
def mock_session():
    session = MagicMock()
    session.wait_for_condition = MagicMock(return_value=True)
    return session


@pytest.fixture
def mock_node_element():
    element = MagicMock()
    element.get_property.side_effect = lambda prop: {
        'text': 'Node 1',
        'expanded': False,
        'selected': False,
        'level': 0,
        'has_children': True
    }.get(prop)
    
    child = MagicMock()
    parent = MagicMock()
    element.find_elements.return_value = [child]
    element.find_element.return_value = parent
    
    return element


@pytest.fixture
def mock_treeview_element():
    element = MagicMock()
    
    root1 = MagicMock()
    root2 = MagicMock()
    element.find_elements.return_value = [root1, root2]
    
    return element


@pytest.fixture
def tree_node(mock_node_element, mock_session):
    return TreeNode(mock_node_element, mock_session)


@pytest.fixture
def tree_view(mock_treeview_element, mock_session):
    return TreeView(mock_treeview_element, mock_session)


def test_node_text(tree_node, mock_node_element):
    """Test getting node text."""
    assert tree_node.text == 'Node 1'
    mock_node_element.get_property.assert_called_with('text')


def test_node_is_expanded(tree_node, mock_node_element):
    """Test checking if node is expanded."""
    assert not tree_node.is_expanded
    mock_node_element.get_property.assert_called_with('expanded')


def test_node_is_selected(tree_node, mock_node_element):
    """Test checking if node is selected."""
    assert not tree_node.is_selected
    mock_node_element.get_property.assert_called_with('selected')


def test_node_level(tree_node, mock_node_element):
    """Test getting node level."""
    assert tree_node.level == 0
    mock_node_element.get_property.assert_called_with('level')


def test_node_has_children(tree_node, mock_node_element):
    """Test checking if node has children."""
    assert tree_node.has_children
    mock_node_element.get_property.assert_called_with('has_children')


def test_node_expand(tree_node):
    """Test expanding node."""
    tree_node.expand()
    tree_node._element.click.assert_called_once()


def test_node_expand_already_expanded(tree_node, mock_node_element):
    """Test expanding already expanded node."""
    mock_node_element.get_property.side_effect = lambda prop: {
        'text': 'Node 1',
        'expanded': True,
        'selected': False,
        'level': 0,
        'has_children': True
    }.get(prop)
    
    tree_node.expand()
    tree_node._element.click.assert_not_called()


def test_node_collapse(tree_node, mock_node_element):
    """Test collapsing node."""
    mock_node_element.get_property.side_effect = lambda prop: {
        'text': 'Node 1',
        'expanded': True,
        'selected': False,
        'level': 0,
        'has_children': True
    }.get(prop)
    
    tree_node.collapse()
    tree_node._element.click.assert_called_once()


def test_node_select(tree_node):
    """Test selecting node."""
    tree_node.select()
    tree_node._element.click.assert_called_once()


def test_node_get_parent(tree_node, mock_node_element):
    """Test getting parent node."""
    parent = tree_node.get_parent()
    assert isinstance(parent, TreeNode)
    mock_node_element.find_element.assert_called_with(by='parent', value=None)


def test_node_get_parent_root(tree_node, mock_node_element):
    """Test getting parent of root node."""
    mock_node_element.get_property.side_effect = lambda prop: {
        'text': 'Root',
        'expanded': False,
        'selected': False,
        'level': 0,
        'has_children': True
    }.get(prop)
    
    assert tree_node.get_parent() is None


def test_node_get_children(tree_node, mock_node_element):
    """Test getting child nodes."""
    children = tree_node.get_children()
    assert len(children) == 1
    assert isinstance(children[0], TreeNode)
    mock_node_element.find_elements.assert_called_with(by='children', value=None)


def test_node_get_children_no_children(tree_node, mock_node_element):
    """Test getting children when node has none."""
    mock_node_element.get_property.side_effect = lambda prop: {
        'text': 'Node 1',
        'expanded': False,
        'selected': False,
        'level': 0,
        'has_children': False
    }.get(prop)
    
    assert tree_node.get_children() == []


def test_treeview_root_nodes(tree_view, mock_treeview_element):
    """Test getting root nodes."""
    nodes = tree_view.root_nodes
    assert len(nodes) == 2
    assert all(isinstance(node, TreeNode) for node in nodes)
    mock_treeview_element.find_elements.assert_called_with(by='type', value='node')


def test_treeview_get_node_by_path(tree_view):
    """Test getting node by path."""
    path = ['Root', 'Child', 'Grandchild']
    node = tree_view.get_node_by_path(path)
    assert isinstance(node, TreeNode)


def test_treeview_get_selected_nodes(tree_view, mock_treeview_element):
    """Test getting selected nodes."""
    nodes = tree_view.get_selected_nodes()
    assert len(nodes) == 2
    assert all(isinstance(node, TreeNode) for node in nodes)
    mock_treeview_element.find_elements.assert_called_with(by='state', value='selected')


def test_treeview_expand_all(tree_view):
    """Test expanding all nodes."""
    tree_view.expand_all()
    # Verification would depend on implementation details


def test_treeview_collapse_all(tree_view):
    """Test collapsing all nodes."""
    tree_view.collapse_all()
    # Verification would depend on implementation details
