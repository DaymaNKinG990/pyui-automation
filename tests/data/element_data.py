"""Test data for UI elements"""

# Default element data
DEFAULT_ELEMENT_DATA = {
    'text': 'test_text',
    'location': {'x': 10, 'y': 20},
    'size': {'width': 100, 'height': 100},
    'attributes': {
        'id': 'test-id',
        'name': 'test-button',
        'class': 'button',
        'value': 'test-value'
    },
    'properties': {
        'tagName': 'button',
        'textContent': 'test_text',
        'innerText': 'test_text',
        'innerHTML': '<button>test_text</button>',
        'outerHTML': '<button class="button">test_text</button>'
    }
}

# Element data with different values
ALTERNATE_ELEMENT_DATA = {
    'text': 'test text',
    'location': {'x': 30, 'y': 40},
    'size': {'width': 50, 'height': 60},
    'attributes': {
        'id': 'alt-id',
        'name': 'alt-button',
        'class': 'alt-button',
        'value': 'alt-value'
    },
    'properties': {
        'tagName': 'div',
        'textContent': 'test text',
        'innerText': 'test text',
        'innerHTML': '<div>test text</div>',
        'outerHTML': '<div class="alt-button">test text</div>'
    }
}

# Screenshot data
SCREENSHOT_DATA = {
    'width': 100,
    'height': 100,
    'channels': 3,
    'dtype': 'uint8'
}

# Window data
WINDOW_DATA = {
    'title': 'Test Window',
    'handle': 'window1',
    'pid': 12345,
    'location': {'x': 0, 'y': 0},
    'size': {'width': 800, 'height': 600}
}

# Process data
PROCESS_DATA = {
    'pid': 12345,
    'name': 'test_app.exe',
    'cpu_percent': 5.0,
    'memory_mb': 100,  # 100MB
    'executable': 'test_app.exe'
}

# Performance data
PERFORMANCE_DATA = {
    'cpu_usage': 5.0,
    'memory_usage': 100,  # MB
    'response_time': 0.5,  # seconds
    'frame_rate': 60,  # fps
    'load_time': 1.0  # seconds
}
