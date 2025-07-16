import pytest
from unittest.mock import MagicMock, patch
import sys
from pyui_automation.core.factory import BackendFactory, ComponentFactory
from pyui_automation.backends.base import BaseBackend
from pyui_automation.input import Keyboard, Mouse
from pyui_automation.core.visual import VisualTester
import comtypes.client
import importlib


_paddleocr_spec = importlib.util.find_spec('paddleocr')
HAS_OCR = _paddleocr_spec is not None


def is_uiautomation_available():
    """Check if Windows UI Automation is available"""
    if sys.platform != 'win32':
        return False
    try:
        comtypes.client.CreateObject("UIAutomationClient.CUIAutomation")
        return True
    except Exception:
        return False


@pytest.fixture
def mock_backend():
    return MagicMock(spec=BaseBackend)

@pytest.mark.skipif(sys.platform == 'darwin', reason="Test not applicable on macOS")
@pytest.mark.skipif(not is_uiautomation_available(), reason="Windows UI Automation not available")
def test_create_backend_for_current_platform():
    """Test creating backend for current platform"""
    backend = BackendFactory.create_backend()
    assert backend is not None

@pytest.mark.skipif(sys.platform == 'darwin', reason="Test not applicable on macOS")
@pytest.mark.skipif(not is_uiautomation_available(), reason="Windows UI Automation not available")
def test_create_backend_explicit():
    """Test creating backend with explicit type"""
    backend = BackendFactory.create_backend("windows")
    assert backend is not None

def test_create_backend_invalid():
    """Test creating backend with invalid type"""
    with pytest.raises(ValueError):
        BackendFactory.create_backend("invalid")

def test_create_keyboard(mock_backend):
    """Test creating keyboard controller"""
    keyboard = ComponentFactory.create_keyboard(mock_backend)
    assert isinstance(keyboard, Keyboard)

def test_create_mouse(mock_backend):
    """Test creating mouse controller"""
    mouse = ComponentFactory.create_mouse(mock_backend)
    assert isinstance(mouse, Mouse)

@pytest.mark.ocr
@pytest.mark.skipif(not HAS_OCR, reason="OCR dependencies not available")
def test_create_ocr_engine():
    """Test creating OCR engine"""
    if not HAS_OCR:  # Extra safety check
        pytest.skip("OCR dependencies not available")
    paddle_mock = MagicMock()
    class MockPaddleOCR:
        def __init__(self, *a, **kw): pass
        def ocr(self, *a, **kw): return [[[]]]
    paddle_mock.PaddleOCR = MockPaddleOCR
    with patch.dict('sys.modules', {'paddleocr': paddle_mock}):
        ocr = ComponentFactory.create_ocr_engine()
        from pyui_automation.ocr import OCREngine
        assert isinstance(ocr, OCREngine)

def test_create_visual_tester():
    """Test creating visual tester"""
    tester = ComponentFactory.create_visual_tester()
    assert isinstance(tester, VisualTester)

def test_create_keyboard_invalid_backend():
    from pyui_automation.core.factory import ComponentFactory
    with pytest.raises(Exception):
        ComponentFactory.create_keyboard(None)
    with pytest.raises(Exception):
        ComponentFactory.create_keyboard('not_a_backend')

def test_create_mouse_invalid_backend():
    from pyui_automation.core.factory import ComponentFactory
    with pytest.raises(Exception):
        ComponentFactory.create_mouse(None)
    with pytest.raises(Exception):
        ComponentFactory.create_mouse('not_a_backend')

def test_create_visual_tester_invalid_dir():
    from pyui_automation.core.factory import ComponentFactory
    with pytest.raises(Exception):
        ComponentFactory.create_visual_tester(123)
    with pytest.raises(Exception):
        ComponentFactory.create_visual_tester(object())

def test_create_ocr_engine_import_error(monkeypatch):
    from pyui_automation.core.factory import ComponentFactory
    import sys
    sys.modules['pyui_automation.ocr'] = None
    monkeypatch.setitem(sys.modules, 'pyui_automation.ocr', None)
    # Переопределяем OCREngine в factory на выбрасывающий ImportError
    import builtins
    orig = builtins.__import__
    def fake_import(name, *args, **kwargs):
        if name == 'pyui_automation.ocr':
            raise ImportError('No OCR')
        return orig(name, *args, **kwargs)
    builtins.__import__ = fake_import
    try:
        with pytest.raises(ImportError):
            ComponentFactory.create_ocr_engine()
    finally:
        builtins.__import__ = orig
