# Advanced Topics

This guide covers advanced topics and techniques for PyUI Automation.

## Custom Element Types

### Creating Custom Elements
```python
from pyui_automation import UIElement, GameElement

class CustomButton(UIElement):
    def __init__(self, backend, locator):
        super().__init__(backend, locator)
        
    def flash(self, times=3):
        """Flash the button by changing its background"""
        for _ in range(times):
            self.set_property('background', 'yellow')
            time.sleep(0.2)
            self.set_property('background', 'white')
            time.sleep(0.2)
            
class GameHealthBar(GameElement):
    def __init__(self, backend, template):
        super().__init__(backend, template)
        
    def get_health_percentage(self):
        """Get current health percentage"""
        region = self.get_region()
        screenshot = self.backend.capture_screen(region=region)
        # Analyze red pixels to determine health
        return self._analyze_health(screenshot)
```

### Element Factories
```python
class ElementFactory:
    @staticmethod
    def create_element(element_type, **kwargs):
        """Create appropriate element based on type"""
        if element_type == 'button':
            return CustomButton(**kwargs)
        elif element_type == 'health_bar':
            return GameHealthBar(**kwargs)
        else:
            return UIElement(**kwargs)
```

## Advanced Image Processing

### Custom Image Recognition
```python
import cv2
import numpy as np

class ImageProcessor:
    @staticmethod
    def find_by_color(image, target_color, tolerance=10):
        """Find regions matching target color"""
        img_array = np.array(image)
        mask = cv2.inRange(
            img_array,
            target_color - tolerance,
            target_color + tolerance
        )
        contours, _ = cv2.findContours(
            mask,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )
        return contours
        
    @staticmethod
    def find_by_shape(image, template, method=cv2.TM_CCOEFF_NORMED):
        """Find regions matching template shape"""
        img_array = np.array(image)
        template_array = np.array(template)
        
        # Convert to grayscale
        img_gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        template_gray = cv2.cvtColor(template_array, cv2.COLOR_RGB2GRAY)
        
        # Find edges
        img_edges = cv2.Canny(img_gray, 50, 200)
        template_edges = cv2.Canny(template_gray, 50, 200)
        
        # Template matching on edges
        result = cv2.matchTemplate(img_edges, template_edges, method)
        return cv2.minMaxLoc(result)
```

### Advanced OCR
```python
from PIL import Image
import pytesseract
import numpy as np

class AdvancedOCR:
    def __init__(self):
        self.config = {
            'lang': 'eng',
            'psm': 3,  # Page segmentation mode
            'oem': 3   # OCR Engine mode
        }
        
    def preprocess_image(self, image):
        """Preprocess image for better OCR"""
        # Convert to numpy array
        img_array = np.array(image)
        
        # Convert to grayscale
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        
        # Apply thresholding
        _, thresh = cv2.threshold(
            gray, 0, 255,
            cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )
        
        # Noise removal
        denoised = cv2.fastNlMeansDenoising(thresh)
        
        return Image.fromarray(denoised)
        
    def recognize_text(self, image, **kwargs):
        """Recognize text with advanced preprocessing"""
        # Update config with kwargs
        config = {**self.config, **kwargs}
        
        # Preprocess image
        processed_img = self.preprocess_image(image)
        
        # Perform OCR
        text = pytesseract.image_to_string(
            processed_img,
            lang=config['lang'],
            config=f'--psm {config["psm"]} --oem {config["oem"]}'
        )
        
        return text.strip()
```

## Custom Input Patterns

### Advanced Mouse Movement
```python
import numpy as np

class HumanMouseMovement:
    @staticmethod
    def bezier_curve(start, end, control_points, steps=100):
        """Generate bezier curve points for smooth movement"""
        points = np.array([start] + control_points + [end])
        t = np.linspace(0, 1, steps)
        
        # De Casteljau's algorithm
        while len(points) > 1:
            points = (1 - t[..., None]) * points[:-1] + \
                    t[..., None] * points[1:]
        
        return points[0]
        
    @staticmethod
    def move_like_human(start, end, duration=1.0):
        """Move mouse in a human-like pattern"""
        # Generate control points
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        
        control1 = (
            start[0] + dx * 0.3 + random.randint(-50, 50),
            start[1] + dy * 0.1 + random.randint(-50, 50)
        )
        control2 = (
            start[0] + dx * 0.7 + random.randint(-50, 50),
            start[1] + dy * 0.9 + random.randint(-50, 50)
        )
        
        # Generate curve points
        points = HumanMouseMovement.bezier_curve(
            start, end, [control1, control2]
        )
        
        # Move mouse along curve
        step_duration = duration / len(points)
        for point in points:
            x, y = map(int, point)
            pyautogui.moveTo(x, y)
            time.sleep(step_duration)
```

### Keyboard Patterns
```python
class KeyboardPatterns:
    @staticmethod
    def type_with_mistakes(text, mistake_probability=0.1):
        """Type text with realistic mistakes and corrections"""
        for char in text:
            if random.random() < mistake_probability:
                # Make a mistake
                wrong_char = random.choice(
                    'qwertyuiopasdfghjklzxcvbnm'
                )
                pyautogui.write(wrong_char)
                time.sleep(random.uniform(0.1, 0.3))
                # Correct the mistake
                pyautogui.press('backspace')
                time.sleep(random.uniform(0.1, 0.3))
            
            # Type correct character
            pyautogui.write(char)
            time.sleep(random.uniform(0.05, 0.2))
            
    @staticmethod
    def type_with_rhythm(text, base_delay=0.1):
        """Type text with a natural rhythm"""
        for i, char in enumerate(text):
            # Longer delay after punctuation
            if i > 0 and text[i-1] in '.!?':
                time.sleep(base_delay * 3)
            # Slight pause after comma
            elif i > 0 and text[i-1] == ',':
                time.sleep(base_delay * 2)
            # Normal typing rhythm
            else:
                time.sleep(base_delay)
            pyautogui.write(char)
```

## Performance Optimization

### Memory Management
```python
class MemoryOptimizer:
    def __init__(self):
        self.cache = {}
        self.cache_size = 1000
        self.cache_hits = 0
        self.cache_misses = 0
        
    def get_cached_element(self, key):
        """Get element from cache with LRU policy"""
        if key in self.cache:
            self.cache_hits += 1
            # Move to end (most recently used)
            value = self.cache.pop(key)
            self.cache[key] = value
            return value
            
        self.cache_misses += 1
        return None
        
    def add_to_cache(self, key, value):
        """Add element to cache with size limit"""
        if len(self.cache) >= self.cache_size:
            # Remove least recently used
            self.cache.pop(next(iter(self.cache)))
        self.cache[key] = value
        
    def get_cache_stats(self):
        """Get cache performance statistics"""
        total = self.cache_hits + self.cache_misses
        hit_rate = self.cache_hits / total if total > 0 else 0
        return {
            'size': len(self.cache),
            'hits': self.cache_hits,
            'misses': self.cache_misses,
            'hit_rate': hit_rate
        }
```

### Parallel Processing
```python
from concurrent.futures import ThreadPoolExecutor
import multiprocessing

class ParallelAutomation:
    def __init__(self, max_workers=None):
        if max_workers is None:
            max_workers = multiprocessing.cpu_count()
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        
    def process_elements_parallel(self, elements, action):
        """Process multiple elements in parallel"""
        futures = []
        for element in elements:
            future = self.executor.submit(action, element)
            futures.append(future)
            
        results = []
        for future in futures:
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                results.append(e)
                
        return results
        
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.executor.shutdown()
```

## Advanced Error Handling

### Error Analysis
```python
class ErrorAnalyzer:
    def __init__(self):
        self.error_history = []
        
    def analyze_error(self, error, context):
        """Analyze error and suggest recovery actions"""
        error_info = {
            'type': type(error).__name__,
            'message': str(error),
            'context': context,
            'timestamp': time.time(),
            'stack_trace': traceback.format_exc()
        }
        
        self.error_history.append(error_info)
        
        return self.suggest_recovery(error_info)
        
    def suggest_recovery(self, error_info):
        """Suggest recovery actions based on error analysis"""
        if 'ElementNotFound' in error_info['type']:
            return [
                'Increase wait timeout',
                'Check element locator',
                'Verify application state'
            ]
        elif 'ConnectionError' in error_info['type']:
            return [
                'Check application running',
                'Verify window title',
                'Restart application'
            ]
        return ['Generic error recovery']
```

### Smart Retry
```python
class SmartRetry:
    def __init__(self):
        self.max_attempts = 3
        self.base_delay = 1
        self.error_analyzer = ErrorAnalyzer()
        
    def retry_with_recovery(self, func, *args, **kwargs):
        """Retry with smart recovery strategies"""
        last_error = None
        
        for attempt in range(self.max_attempts):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_error = e
                
                # Analyze error
                recovery_actions = self.error_analyzer.analyze_error(
                    e, {'attempt': attempt}
                )
                
                # Try recovery actions
                for action in recovery_actions:
                    try:
                        self.execute_recovery(action)
                        break
                    except Exception:
                        continue
                        
                # Wait before next attempt
                time.sleep(self.base_delay * (2 ** attempt))
                
        raise last_error
        
    def execute_recovery(self, action):
        """Execute recovery action"""
        if action == 'Increase wait timeout':
            # Implement timeout increase
            pass
        elif action == 'Restart application':
            # Implement application restart
            pass
        # Add more recovery actions
```

## Testing and Validation

### Test Framework
```python
class AutomationTest:
    def __init__(self):
        self.setup_actions = []
        self.test_actions = []
        self.cleanup_actions = []
        self.assertions = []
        
    def add_setup(self, action):
        """Add setup action"""
        self.setup_actions.append(action)
        
    def add_test(self, action):
        """Add test action"""
        self.test_actions.append(action)
        
    def add_cleanup(self, action):
        """Add cleanup action"""
        self.cleanup_actions.append(action)
        
    def add_assertion(self, assertion):
        """Add test assertion"""
        self.assertions.append(assertion)
        
    def run(self):
        """Run the test"""
        try:
            # Setup
            for action in self.setup_actions:
                action()
                
            # Test
            results = []
            for action in self.test_actions:
                result = action()
                results.append(result)
                
            # Assertions
            for assertion in self.assertions:
                assertion(results)
                
        finally:
            # Cleanup
            for action in self.cleanup_actions:
                try:
                    action()
                except Exception as e:
                    print(f"Cleanup error: {e}")
```

### Validation Framework
```python
class ValidationFramework:
    def __init__(self):
        self.validators = {}
        
    def register_validator(self, name, validator):
        """Register a validator function"""
        self.validators[name] = validator
        
    def validate(self, data, validators=None):
        """Run validation on data"""
        results = {}
        
        # Use specified validators or all
        validators = validators or self.validators.keys()
        
        for name in validators:
            if name in self.validators:
                try:
                    result = self.validators[name](data)
                    results[name] = {
                        'success': True,
                        'result': result
                    }
                except Exception as e:
                    results[name] = {
                        'success': False,
                        'error': str(e)
                    }
                    
        return results
```

## Best Practices

1. **Use Custom Elements for Complex UI Patterns**
```python
class LoginForm(UIElement):
    def login(self, username, password):
        self.find_element(name="username").type_text(username)
        self.find_element(name="password").type_text(password)
        self.find_element(name="submit").click()
```

2. **Implement Robust Error Handling**
```python
def safe_automation(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ElementNotFoundError:
            # Handle element not found
            pass
        except TimeoutError:
            # Handle timeout
            pass
        except Exception as e:
            # Handle unexpected errors
            logger.error(f"Unexpected error: {e}")
            raise
    return wrapper
```

3. **Use Performance Monitoring**
```python
@performance_monitor
def complex_automation():
    with timer("setup"):
        # Setup code
        pass
        
    with timer("main_action"):
        # Main automation
        pass
        
    with timer("cleanup"):
        # Cleanup
        pass
```

4. **Implement Proper Cleanup**
```python
class AutomationContext:
    def __init__(self):
        self.resources = []
        
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        for resource in reversed(self.resources):
            try:
                resource.cleanup()
            except Exception as e:
                logger.error(f"Cleanup error: {e}")
```

## Next Steps

- Explore [Game Automation](./game_automation.md)
- Check out the [API Reference](./api_reference.md)
- Learn about specific use cases in our [Examples](./examples.md)
