from .input import InputService

class InputServiceImpl(InputService):
    """Implementation of InputService for keyboard and mouse actions on UI elements."""
    def __init__(self, keyboard, mouse):
        """Initialize input service implementation."""
        self.keyboard = keyboard
        self.mouse = mouse

    def click(self, element):
        x, y = element.center if hasattr(element, 'center') else (element.location['x'], element.location['y'])
        self.mouse.click(x, y)

    def double_click(self, element):
        x, y = element.center if hasattr(element, 'center') else (element.location['x'], element.location['y'])
        self.mouse.double_click(x, y)

    def right_click(self, element):
        x, y = element.center if hasattr(element, 'center') else (element.location['x'], element.location['y'])
        self.mouse.right_click(x, y)

    def type_text(self, element, text, interval=0.0):
        self.click(element)
        self.keyboard.type_text(text, interval)

    def send_keys(self, element, *keys):
        self.click(element)
        for key in keys:
            self.keyboard.send_keys(key)

    def press_key(self, key: str) -> None:
        self.keyboard.press_key(key)

    def release_key(self, key: str) -> None:
        self.keyboard.release_key(key)

    def move_mouse(self, x: int, y: int) -> None:
        self.mouse.move(x, y)

    def click_mouse(self, x: int, y: int, button: str = "left") -> None:
        self.mouse.click(x, y, button) 