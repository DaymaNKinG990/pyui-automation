import pytest
from unittest.mock import MagicMock, patch
from PIL import Image as PILImage
from pyui_automation.elements.image import Image


@pytest.fixture
def mock_session():
    session = MagicMock()
    session.wait_for_condition = MagicMock(return_value=True)
    session.capture_element = MagicMock(return_value=MagicMock(spec=PILImage.Image))
    session.compare_images = MagicMock(return_value=1.0)
    return session

@pytest.fixture
def mock_image_element():
    element = MagicMock()
    # Set up default property values
    element.get_property.side_effect = lambda prop: {
        'alt_text': 'Test Image',
        'source': '/path/to/image.png',
        'width': 100,
        'height': 200,
        'visible': True
    }.get(prop)
    return element

@pytest.fixture
def image(mock_image_element, mock_session):
    return Image(mock_image_element, mock_session)

def test_init(image, mock_image_element, mock_session):
    """Test image initialization."""
    assert image._element == mock_image_element
    assert image._session == mock_session

def test_alt_text(image, mock_image_element):
    """Test getting alternative text."""
    assert image.alt_text == 'Test Image'
    mock_image_element.get_property.assert_called_with('alt_text')

def test_source(image, mock_image_element):
    """Test getting image source."""
    assert image.source == '/path/to/image.png'
    mock_image_element.get_property.assert_called_with('source')

def test_size(image, mock_image_element):
    """Test getting image dimensions."""
    assert image.size == (100, 200)
    mock_image_element.get_property.assert_any_call('width')
    mock_image_element.get_property.assert_any_call('height')

def test_is_visible(image, mock_image_element):
    """Test checking if image is visible."""
    assert image.is_visible
    mock_image_element.get_property.assert_called_with('visible')

def test_capture(image, mock_session):
    """Test capturing image content."""
    captured = image.capture()
    assert isinstance(captured, MagicMock)  # Would be PIL.Image.Image in real usage
    mock_session.capture_element.assert_called_once_with(image._element)

@patch('PIL.Image.Image.save')
def test_save_as(mock_save, image, mock_session):
    """Test saving image to file."""
    image.save_as('test.png')
    mock_session.capture_element.assert_called_once()
    # Note: We can't easily verify the save call because we're using a MagicMock for PIL.Image

def test_compare_to(image, mock_session):
    """Test comparing with another image."""
    other_image = MagicMock(spec=PILImage.Image)
    result = image.compare_to(other_image, threshold=0.9)
    assert result == 1.0
    mock_session.compare_images.assert_called_once_with(
        mock_session.capture_element.return_value,
        other_image,
        threshold=0.9
    )

class ImageMock(Image):
    def __init__(self, native_element, session, is_visible=True, size=(100, 100)):
        super().__init__(native_element, session)
        self._mock_is_visible = is_visible
        self._mock_size = size
    @property
    def is_visible(self):
        return self._mock_is_visible
    @property
    def size(self):
        return self._mock_size

def test_wait_until_loaded(mock_image_element, mock_session):
    """Test waiting for image to load (без patch.object, через double)."""
    image = ImageMock(mock_image_element, mock_session, is_visible=True, size=(100, 100))
    assert image.wait_until_loaded(timeout=5.0)
    mock_session.wait_for_condition.assert_called_once()
    condition_func = mock_session.wait_for_condition.call_args[0][0]
    image._mock_is_visible = True
    image._mock_size = (100, 100)
    assert condition_func()
    image._mock_is_visible = False
    image._mock_size = (100, 100)
    assert not condition_func()
    image._mock_is_visible = True
    image._mock_size = (0, 0)
    assert not condition_func()

def test_wait_until_matches(image, mock_session):
    """Test waiting for image to match another."""
    other_image = MagicMock(spec=PILImage.Image)
    assert image.wait_until_matches(other_image, threshold=0.9, timeout=5.0)
    
    mock_session.wait_for_condition.assert_called_once()
    condition_func = mock_session.wait_for_condition.call_args[0][0]
    
    # Test condition function with different similarity scores
    mock_session.compare_images.return_value = 0.95
    assert condition_func()
    
    mock_session.compare_images.return_value = 0.85
    assert not condition_func()

def test_wait_until_matches_custom_threshold(image, mock_session):
    """Test waiting for image to match with custom threshold."""
    other_image = MagicMock(spec=PILImage.Image)
    threshold = 0.8
    assert image.wait_until_matches(other_image, threshold=threshold, timeout=5.0)
    
    condition_func = mock_session.wait_for_condition.call_args[0][0]
    
    mock_session.compare_images.return_value = 0.85
    assert condition_func()  # Should pass with lower threshold
    
    mock_session.compare_images.return_value = 0.75
    assert not condition_func()  # Should fail even with lower threshold
