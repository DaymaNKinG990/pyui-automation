import pytest
from unittest.mock import MagicMock
from pyui_automation.game_elements.talent_tree import TalentNode, TalentSpec, TalentTree

@pytest.fixture
def mock_node_element():
    el = MagicMock()
    el.get_property.side_effect = lambda key: {
        'name': 'Fireball',
        'description': 'Cast a fireball',
        'current_rank': 1,
        'max_rank': 3,
        'available': True,
        'prerequisites': ['Pyromancy'],
    }.get(key)
    el.find_element.side_effect = lambda *a, **kw: None
    return el

@pytest.fixture
def mock_spec_element():
    el = MagicMock()
    el.get_property.side_effect = lambda key: {
        'name': 'Fire',
        'description': 'Fire spec',
        'active': False,
        'points_spent': 5,
    }.get(key)
    el.find_element.side_effect = lambda *a, **kw: None
    return el

@pytest.fixture
def mock_tree_element():
    el = MagicMock()
    el.get_property.side_effect = lambda key: 2 if key == 'available_points' else 10 if key == 'level_requirement' else None
    el.find_elements.side_effect = lambda *a, **kw: []
    el.find_element.side_effect = lambda *a, **kw: None
    return el

@pytest.fixture
def mock_session():
    return MagicMock()

@pytest.fixture
def node(mock_node_element, mock_session):
    return TalentNode(mock_node_element, mock_session)

@pytest.fixture
def spec(mock_spec_element, mock_session):
    return TalentSpec(mock_spec_element, mock_session)

@pytest.fixture
def tree(mock_tree_element, mock_session):
    return TalentTree(mock_tree_element, mock_session)

def test_node_properties(node):
    assert node.name == 'Fireball'
    assert node.description == 'Cast a fireball'
    assert node.rank == (1, 3)
    assert node.is_available is True
    assert node.prerequisites == ['Pyromancy']
    assert node.is_maxed is False

def test_node_is_maxed(node, mock_node_element):
    mock_node_element.get_property.side_effect = lambda key: 3 if key == 'current_rank' or key == 'max_rank' else True if key == 'available' else None
    assert node.is_maxed is True

def test_node_learn_success(node, mock_node_element):
    mock_node_element.get_property.side_effect = lambda key: True if key == 'available' else 1 if key == 'current_rank' else 3 if key == 'max_rank' else None
    btn = MagicMock()
    btn.is_enabled.return_value = True
    btn.click = MagicMock()
    mock_node_element.find_element.side_effect = lambda *a, **kw: btn if kw.get('value') == 'learn_button' else None
    assert node.learn() is True
    assert btn.click.called

def test_node_learn_not_available(node, mock_node_element):
    mock_node_element.get_property.side_effect = lambda key: False if key == 'available' else 1 if key == 'current_rank' else 3 if key == 'max_rank' else None
    assert node.learn() is False

def test_node_learn_maxed(node, mock_node_element):
    mock_node_element.get_property.side_effect = lambda key: True if key == 'available' else 3 if key == 'current_rank' or key == 'max_rank' else None
    assert node.learn() is False

def test_node_learn_button_disabled(node, mock_node_element):
    mock_node_element.get_property.side_effect = lambda key: True if key == 'available' else 1 if key == 'current_rank' else 3 if key == 'max_rank' else None
    btn = MagicMock()
    btn.is_enabled.return_value = False
    mock_node_element.find_element.side_effect = lambda *a, **kw: btn if kw.get('value') == 'learn_button' else None
    assert node.learn() is False

def test_node_get_property_exception(node, mock_node_element):
    mock_node_element.get_property.side_effect = Exception('fail')
    with pytest.raises(Exception):
        _ = node.name

def test_node_learn_find_element_exception(node, mock_node_element):
    mock_node_element.get_property.side_effect = lambda key: True if key == 'available' else 1 if key == 'current_rank' else 3 if key == 'max_rank' else None
    mock_node_element.find_element.side_effect = Exception('fail')
    with pytest.raises(Exception):
        node.learn()

def test_spec_properties(spec):
    assert spec.name == 'Fire'
    assert spec.description == 'Fire spec'
    assert spec.is_active is False
    assert spec.points_spent == 5

def test_spec_activate_success(spec, mock_spec_element):
    mock_spec_element.get_property.side_effect = lambda key: False if key == 'active' else None
    btn = MagicMock()
    btn.is_enabled.return_value = True
    btn.click = MagicMock()
    mock_spec_element.find_element.side_effect = lambda *a, **kw: btn if kw.get('value') == 'activate_button' else None
    assert spec.activate() is True
    assert btn.click.called

def test_spec_activate_already_active(spec, mock_spec_element):
    mock_spec_element.get_property.side_effect = lambda key: True if key == 'active' else None
    assert spec.activate() is True

def test_spec_activate_button_disabled(spec, mock_spec_element):
    mock_spec_element.get_property.side_effect = lambda key: False if key == 'active' else None
    btn = MagicMock()
    btn.is_enabled.return_value = False
    mock_spec_element.find_element.side_effect = lambda *a, **kw: btn if kw.get('value') == 'activate_button' else None
    assert spec.activate() is False

def test_spec_get_property_exception(spec, mock_spec_element):
    mock_spec_element.get_property.side_effect = Exception('fail')
    with pytest.raises(Exception):
        _ = spec.name

def test_spec_activate_find_element_exception(spec, mock_spec_element):
    mock_spec_element.get_property.side_effect = lambda key: False if key == 'active' else None
    mock_spec_element.find_element.side_effect = Exception('fail')
    with pytest.raises(Exception):
        spec.activate()

def test_tree_properties(tree):
    assert tree.available_points == 2
    assert tree.level_requirement == 10

def test_tree_specializations_empty(tree, mock_tree_element):
    mock_tree_element.find_elements.side_effect = lambda *a, **kw: []
    assert tree.specializations == []

def test_tree_active_spec_none(tree, mock_tree_element):
    mock_tree_element.find_elements.side_effect = lambda *a, **kw: []
    assert tree.active_spec is None

def test_tree_get_talent_none(tree, mock_tree_element):
    mock_tree_element.find_element.side_effect = lambda *a, **kw: None
    assert tree.get_talent('Fireball') is None

def test_tree_get_available_talents_empty(tree, mock_tree_element):
    mock_tree_element.find_elements.side_effect = lambda *a, **kw: []
    assert tree.get_available_talents() == []

def test_tree_reset_talents_success(tree, mock_tree_element):
    btn = MagicMock()
    btn.is_enabled.return_value = True
    btn.click = MagicMock()
    confirm = MagicMock()
    confirm.click = MagicMock()
    def find_element_side_effect(*a, **kw):
        if kw.get('value') == 'reset_button':
            return btn
        if kw.get('value') == 'confirm_reset':
            return confirm
        return None
    mock_tree_element.find_element.side_effect = find_element_side_effect
    assert tree.reset_talents() is True
    assert btn.click.called
    assert confirm.click.called

def test_tree_reset_talents_button_disabled(tree, mock_tree_element):
    btn = MagicMock()
    btn.is_enabled.return_value = False
    mock_tree_element.find_element.side_effect = lambda *a, **kw: btn if kw.get('value') == 'reset_button' else None
    assert tree.reset_talents() is False

def test_tree_reset_talents_no_confirm(tree, mock_tree_element):
    btn = MagicMock()
    btn.is_enabled.return_value = True
    btn.click = MagicMock()
    mock_tree_element.find_element.side_effect = lambda *a, **kw: btn if kw.get('value') == 'reset_button' else None
    assert tree.reset_talents() is False

def test_tree_get_property_exception(tree, mock_tree_element):
    mock_tree_element.get_property.side_effect = Exception('fail')
    with pytest.raises(Exception):
        _ = tree.available_points

def test_tree_find_element_exception(tree, mock_tree_element):
    mock_tree_element.find_element.side_effect = Exception('fail')
    with pytest.raises(Exception):
        tree.get_talent('Fireball')

def test_tree_find_elements_exception(tree, mock_tree_element):
    mock_tree_element.find_elements.side_effect = Exception('fail')
    with pytest.raises(Exception):
        tree.get_available_talents() 