# OCR Architecture

## 🏗️ **Новая архитектура OCR модуля**

OCR модуль был полностью реструктурирован для соответствия принципам SOLID и лучшим практикам архитектуры.

## 📁 **Структура файлов**

```
pyui_automation/ocr/
├── __init__.py          # Экспорты и convenience функции
├── models.py            # Модели данных (OCRResult, TextLocation)
├── preprocessing.py     # Предобработка изображений
├── engine.py           # Основной OCR движок (PaddleOCR)
├── stub.py             # Заглушка для тестов
└── unified.py          # Унифицированный движок
```

## 🎯 **Принципы SOLID**

### **Single Responsibility Principle (SRP)**
Каждый класс имеет одну ответственность:

- **`ImagePreprocessor`** - только предобработка изображений
- **`OCREngine`** - только распознавание текста с PaddleOCR
- **`StubOCREngine`** - только предоставление тестовых данных
- **`UnifiedOCREngine`** - только выбор и делегирование к реализации
- **`OCRResult`** - только хранение результата OCR
- **`TextLocation`** - только хранение местоположения текста

### **Open/Closed Principle (OCP)**
Легко расширять новыми OCR движками без изменения существующего кода:

```python
class CustomOCREngine(IOCRService):
    def recognize_text(self, image, preprocess=False):
        # Кастомная реализация
        pass

# Использование
unified = UnifiedOCREngine()
unified.set_implementation(CustomOCREngine())
```

### **Liskov Substitution Principle (LSP)**
Все OCR движки взаимозаменяемы:

```python
# Любой движок можно использовать одинаково
engines = [OCREngine(), StubOCREngine(), CustomOCREngine()]
for engine in engines:
    text = engine.recognize_text(image)
```

### **Interface Segregation Principle (ISP)**
Интерфейсы разделены по ответственности:

- **`ITextRecognition`** - распознавание текста
- **`ITextLocation`** - поиск местоположения
- **`ITextVerification`** - проверка наличия
- **`IImagePreprocessing`** - предобработка

### **Dependency Inversion Principle (DIP)**
Зависимости от абстракций:

```python
class UnifiedOCREngine:
    def __init__(self, implementation: Optional[IOCRService] = None):
        # Зависит от интерфейса, а не от конкретной реализации
```

## 🔧 **Основные компоненты**

### **OCRResult** - Модель результата
```python
from pyui_automation.ocr import OCRResult

result = OCRResult(
    text="Hello World",
    confidence=0.95,
    bbox=(10, 10, 100, 30)
)
```

### **TextLocation** - Модель местоположения
```python
from pyui_automation.ocr import TextLocation

location = TextLocation(
    x=10, y=10, width=100, height=30,
    text="Hello World", confidence=0.95
)
```

### **ImagePreprocessor** - Предобработка
```python
from pyui_automation.ocr import ImagePreprocessor

preprocessor = ImagePreprocessor()
enhanced_image = preprocessor.preprocess(image)
contrast_image = preprocessor.enhance_contrast(image)
denoised_image = preprocessor.remove_noise(image)
resized_image = preprocessor.resize_for_ocr(image)
```

### **OCREngine** - Основной движок
```python
from pyui_automation.ocr import OCREngine

engine = OCREngine()
engine.set_languages(['en', 'ru'])
text = engine.recognize_text(image, preprocess=True)
```

### **StubOCREngine** - Тестовая заглушка
```python
from pyui_automation.ocr import StubOCREngine, OCRResult

stub = StubOCREngine()
stub.add_test_data("login", OCRResult("login", 0.95, (100, 100, 60, 20)))
text = stub.recognize_text(image)  # Возвращает "sample text"
```

### **UnifiedOCREngine** - Унифицированный интерфейс
```python
from pyui_automation.ocr import UnifiedOCREngine

# Автоматический выбор реализации
unified = UnifiedOCREngine()

# Или указание конкретной реализации
from .engine import OCREngine
unified = UnifiedOCREngine(OCREngine())

# Информация о реализации
info = unified.get_implementation_info()
print(f"Using: {info['type']}")
```

## 🚀 **Использование**

### **Простое использование**
```python
from pyui_automation.ocr import recognize_text, set_languages

# Настройка языков
set_languages(['en', 'ru'])

# Распознавание текста
text = recognize_text("screenshot.png")
```

### **Продвинутое использование**
```python
from pyui_automation.ocr import UnifiedOCREngine, OCREngine

# Создание движка
engine = UnifiedOCREngine()

# Распознавание с предобработкой
text = engine.recognize_text(image, preprocess=True)

# Поиск местоположения текста
locations = engine.find_text_location(element, "Login")

# Проверка наличия текста
has_text = engine.verify_text_presence(element, "Welcome")

# Получение всего текста
all_text = engine.get_all_text(element)
```

### **Работа с элементами**
```python
from pyui_automation import PyUIAutomation

app = PyUIAutomation("app.exe")

# OCR из элемента
text = app.get_ocr_text("elementName")

# Настройка языков
app.ocr_set_languages(['en', 'ru'])

# Распознавание из изображения
text = app.ocr_recognize_text("image.png")
```

## 🧪 **Тестирование**

### **Использование заглушки в тестах**
```python
import pytest
from pyui_automation.ocr import StubOCREngine, OCRResult

@pytest.fixture
def ocr_stub():
    stub = StubOCREngine()
    stub.add_test_data("login", OCRResult("login", 0.95, (100, 100, 60, 20)))
    return stub

def test_ocr_recognition(ocr_stub):
    text = ocr_stub.recognize_text("any_image.png")
    assert text == "sample text"
```

### **Мокирование OCR**
```python
from unittest.mock import Mock
from pyui_automation.ocr import UnifiedOCREngine

# Создание мока
mock_engine = Mock()
mock_engine.recognize_text.return_value = "mocked text"

# Использование мока
unified = UnifiedOCREngine(mock_engine)
text = unified.recognize_text("image.png")
assert text == "mocked text"
```

## 🔄 **Миграция с старой архитектуры**

### **Старый код:**
```python
from pyui_automation.services.ocr import OCREngine

ocr = OCREngine()
text = ocr.recognize_text("image.png")
```

### **Новый код:**
```python
from pyui_automation.ocr import UnifiedOCREngine

# Автоматический выбор лучшей реализации
ocr = UnifiedOCREngine()
text = ocr.recognize_text("image.png")

# Или прямое использование
from pyui_automation.ocr import OCREngine
ocr = OCREngine()
text = ocr.recognize_text("image.png")
```

## ✅ **Преимущества новой архитектуры**

1. **Чистота кода** - каждый класс имеет одну ответственность
2. **Тестируемость** - легко мокировать и тестировать
3. **Расширяемость** - легко добавлять новые OCR движки
4. **Гибкость** - можно выбирать реализацию
5. **Надежность** - автоматический fallback на заглушку
6. **Читаемость** - понятная структура файлов
7. **Соответствие SOLID** - все принципы соблюдены

## 🚨 **Важные замечания**

1. **PaddleOCR** - для реального OCR требуется установка: `pip install paddleocr`
2. **Fallback** - если PaddleOCR недоступен, автоматически используется заглушка
3. **Производительность** - предобработка может улучшить точность OCR
4. **Языки** - поддерживаются множественные языки
5. **Тестирование** - всегда используйте заглушки в unit-тестах 