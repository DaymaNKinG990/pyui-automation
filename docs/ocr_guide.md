# OCR Guide

## 🔤 **Обзор OCR системы**

PyUI Automation предоставляет унифицированную систему OCR (Optical Character Recognition) для распознавания текста из изображений и UI элементов. Система автоматически выбирает оптимальную реализацию и поддерживает множественные языки.

## 🏗️ **Архитектура OCR**

### **Унифицированный OCR Engine**

```python
from pyui_automation.services.ocr import OCREngine

# Создание OCR движка
ocr = OCREngine()

# Автоматический выбор реализации
# - PaddleOCR (основная реализация)
# - StubOCREngine (для тестирования)
# - EasyOCR (альтернативная реализация)
```

### **Поддерживаемые реализации**

1. **PaddleOCR** - основная реализация с высокой точностью
2. **EasyOCR** - альтернативная реализация
3. **StubOCREngine** - заглушка для тестирования
4. **Tesseract** - классическая реализация

## 🚀 **Базовое использование**

### **Распознавание текста из изображения**

```python
from pyui_automation.services.ocr import OCREngine
import numpy as np

# Создание OCR движка
ocr = OCREngine()

# Распознавание из файла
text = ocr.recognize_text("screenshot.png")
print(f"Распознанный текст: {text}")

# Распознавание из numpy array
image = np.array(...)  # Ваше изображение
text = ocr.recognize_text(image)
print(f"Распознанный текст: {text}")

# Распознавание с предобработкой
text = ocr.recognize_text("screenshot.png", preprocess=True)
```

### **Распознавание текста из UI элемента**

```python
from pyui_automation.core import AutomationSession

# Создание сессии
session = AutomationSession(backend)

# Поиск элемента с текстом
element = session.find_element_by_object_name("text_element")

# Распознавание текста из элемента
text = session.ocr.read_text_from_element(element)
print(f"Текст элемента: {text}")

# Распознавание с предобработкой
text = session.ocr.read_text_from_element(element, preprocess=True)
```

## 🌍 **Многоязычная поддержка**

### **Настройка языков**

```python
# Установка языков для распознавания
ocr.set_languages(['en', 'ru', 'de', 'fr'])

# Установка одного языка
ocr.set_language('en')

# Получение текущих языков
languages = ocr.get_languages()
print(f"Поддерживаемые языки: {languages}")
```

### **Примеры многоязычного распознавания**

```python
# Английский текст
ocr.set_languages(['en'])
english_text = ocr.recognize_text("english_screenshot.png")

# Русский текст
ocr.set_languages(['ru'])
russian_text = ocr.recognize_text("russian_screenshot.png")

# Многоязычный текст
ocr.set_languages(['en', 'ru'])
mixed_text = ocr.recognize_text("mixed_screenshot.png")
```

## 🔍 **Расширенные возможности**

### **Поиск расположения текста**

```python
# Поиск координат текста в элементе
locations = session.ocr.find_text_location(
    element=element,
    text="искомый текст",
    confidence_threshold=0.8
)

for location in locations:
    x, y, width, height = location
    print(f"Текст найден в области: ({x}, {y}, {width}, {height})")
```

### **Получение всех текстов с координатами**

```python
# Получение всех текстов с их расположением
texts = session.ocr.get_all_text(
    element=element,
    confidence_threshold=0.7
)

for text_info in texts:
    print(f"Текст: '{text_info['text']}'")
    print(f"Координаты: {text_info['bbox']}")
    print(f"Уверенность: {text_info['confidence']:.2f}")
    print(f"Язык: {text_info['language']}")
```

### **Проверка наличия текста**

```python
# Проверка наличия конкретного текста
is_present = session.ocr.verify_text_presence(
    element=element,
    text="ожидаемый текст",
    confidence_threshold=0.8
)

if is_present:
    print("Текст найден!")
else:
    print("Текст не найден")
```

## 🎨 **Предобработка изображений**

### **Встроенная предобработка**

```python
# Автоматическая предобработка
text = ocr.recognize_text("image.png", preprocess=True)

# Предобработка включает:
# - Нормализацию яркости
# - Улучшение контраста
# - Удаление шума
# - Масштабирование
```

### **Кастомная предобработка**

```python
import cv2
import numpy as np

def custom_preprocess(image):
    """Кастомная предобработка изображения"""
    # Конвертация в оттенки серого
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Применение фильтра Гаусса
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Адаптивная пороговая обработка
    thresh = cv2.adaptiveThreshold(
        blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY, 11, 2
    )
    
    return thresh

# Применение кастомной предобработки
image = cv2.imread("image.png")
processed_image = custom_preprocess(image)
text = ocr.recognize_text(processed_image)
```

## 📊 **Настройка точности**

### **Пороги уверенности**

```python
# Высокий порог уверенности (строгий)
text = ocr.recognize_text("image.png", confidence_threshold=0.9)

# Средний порог уверенности (баланс)
text = ocr.recognize_text("image.png", confidence_threshold=0.7)

# Низкий порог уверенности (мягкий)
text = ocr.recognize_text("image.png", confidence_threshold=0.5)
```

### **Фильтрация результатов**

```python
# Получение всех результатов с фильтрацией
results = ocr.recognize_text_with_confidence("image.png")

# Фильтрация по уверенности
high_confidence_results = [
    result for result in results 
    if result['confidence'] > 0.8
]

# Фильтрация по длине текста
long_text_results = [
    result for result in results 
    if len(result['text']) > 3
]
```

## 🔧 **Конфигурация OCR**

### **Настройка параметров**

```python
# Создание OCR с кастомными параметрами
ocr = OCREngine(
    languages=['en', 'ru'],
    confidence_threshold=0.7,
    preprocess=True,
    use_gpu=False  # Использование CPU вместо GPU
)

# Изменение параметров после создания
ocr.set_confidence_threshold(0.8)
ocr.set_preprocessing(True)
ocr.set_gpu_usage(True)
```

### **Выбор реализации**

```python
from pyui_automation.services.ocr import OCREngine, OCREngineType

# Явный выбор реализации
ocr = OCREngine(engine_type=OCREngineType.PADDLE_OCR)
ocr = OCREngine(engine_type=OCREngineType.EASY_OCR)
ocr = OCREngine(engine_type=OCREngineType.TESSERACT)

# Автоматический выбор (по умолчанию)
ocr = OCREngine()  # Автоматически выбирает лучшую доступную реализацию
```

## 🧪 **Тестирование OCR**

### **Тестирование с заглушкой**

```python
from pyui_automation.services.ocr import StubOCREngine

# Создание заглушки для тестирования
stub_ocr = StubOCREngine()

# Настройка ожидаемых результатов
stub_ocr.set_expected_text("test text")
stub_ocr.set_expected_confidence(0.9)

# Тестирование
text = stub_ocr.recognize_text("any_image.png")
assert text == "test text"
```

### **Тестирование точности**

```python
def test_ocr_accuracy():
    """Тест точности OCR"""
    ocr = OCREngine()
    
    # Тестовые изображения с известным текстом
    test_cases = [
        ("test_image_1.png", "Expected text 1"),
        ("test_image_2.png", "Expected text 2"),
        ("test_image_3.png", "Expected text 3"),
    ]
    
    for image_path, expected_text in test_cases:
        recognized_text = ocr.recognize_text(image_path)
        
        # Проверка точности
        accuracy = calculate_text_similarity(recognized_text, expected_text)
        assert accuracy > 0.8, f"Low accuracy: {accuracy} for {image_path}"
```

## 🎯 **Практические примеры**

### **Автоматизация формы с OCR**

```python
def fill_form_with_ocr(session):
    """Заполнение формы с использованием OCR"""
    
    # Поиск полей формы
    name_field = session.find_element_by_object_name("name_field")
    email_field = session.find_element_by_object_name("email_field")
    
    # Распознавание текста из полей
    current_name = session.ocr.read_text_from_element(name_field)
    current_email = session.ocr.read_text_from_element(email_field)
    
    print(f"Текущее имя: {current_name}")
    print(f"Текущий email: {current_email}")
    
    # Проверка и заполнение полей
    if not current_name:
        name_field.type_text("John Doe")
    
    if not current_email:
        email_field.type_text("john@example.com")
```

### **Валидация UI с OCR**

```python
def validate_ui_text(session):
    """Валидация текста в UI с помощью OCR"""
    
    # Ожидаемые тексты
    expected_texts = [
        "Welcome",
        "Login",
        "Password",
        "Submit"
    ]
    
    # Проверка каждого ожидаемого текста
    for expected_text in expected_texts:
        is_present = session.ocr.verify_text_presence(
            element=None,  # Поиск по всему экрану
            text=expected_text,
            confidence_threshold=0.8
        )
        
        if not is_present:
            print(f"❌ Текст '{expected_text}' не найден")
        else:
            print(f"✅ Текст '{expected_text}' найден")
```

### **Извлечение данных из таблицы**

```python
def extract_table_data(session):
    """Извлечение данных из таблицы с помощью OCR"""
    
    # Поиск таблицы
    table = session.find_element_by_object_name("data_table")
    
    # Получение всех текстов в таблице
    texts = session.ocr.get_all_text(table, confidence_threshold=0.7)
    
    # Структурирование данных
    table_data = []
    current_row = []
    
    for text_info in texts:
        text = text_info['text']
        bbox = text_info['bbox']
        
        # Простая логика группировки по строкам
        if len(current_row) == 0 or bbox[1] - current_row[-1]['bbox'][1] < 20:
            current_row.append(text_info)
        else:
            table_data.append(current_row)
            current_row = [text_info]
    
    if current_row:
        table_data.append(current_row)
    
    return table_data
```

## 🚨 **Обработка ошибок**

### **Обработка ошибок OCR**

```python
from pyui_automation.core.exceptions import OCRError

try:
    text = session.ocr.recognize_text("image.png")
except OCRError as e:
    print(f"Ошибка OCR: {e}")
    # Fallback стратегия
    text = "fallback_text"
except Exception as e:
    print(f"Неожиданная ошибка: {e}")
```

### **Проверка качества изображения**

```python
def check_image_quality(image_path):
    """Проверка качества изображения для OCR"""
    import cv2
    import numpy as np
    
    image = cv2.imread(image_path)
    
    # Проверка разрешения
    height, width = image.shape[:2]
    if width < 100 or height < 100:
        return False, "Изображение слишком маленькое"
    
    # Проверка контраста
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    contrast = np.std(gray)
    if contrast < 30:
        return False, "Низкий контраст"
    
    # Проверка размытия
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    if laplacian_var < 100:
        return False, "Изображение размыто"
    
    return True, "Изображение подходит для OCR"
```

## 🎯 **Best Practices**

### **Оптимизация точности**
1. **Используйте качественные изображения** с высоким разрешением
2. **Обеспечивайте хорошее освещение** и контраст
3. **Избегайте размытых изображений** и шума
4. **Используйте предобработку** для сложных изображений

### **Производительность**
1. **Кэшируйте результаты OCR** для повторяющихся изображений
2. **Используйте GPU** для больших объемов данных
3. **Оптимизируйте размер изображений** перед распознаванием
4. **Параллелизуйте обработку** множественных изображений

### **Надежность**
1. **Устанавливайте разумные пороги уверенности** (0.7-0.8)
2. **Используйте fallback стратегии** при ошибках
3. **Валидируйте результаты** OCR
4. **Логируйте ошибки** для отладки

### **Многоязычность**
1. **Указывайте правильные языки** для вашего контента
2. **Тестируйте на разных языках** для валидации
3. **Учитывайте особенности шрифтов** разных языков
4. **Используйте языковые модели** для улучшения точности

## 📚 **Примеры интеграции**

### **Полный пример автоматизации с OCR**

```python
from pyui_automation.core import DIAutomationManager, AutomationSession
from pyui_automation.core.factory import BackendFactory
from pyui_automation.application import Application

def automate_with_ocr():
    """Полная автоматизация с использованием OCR"""
    
    # Создание менеджера и сессии
    manager = DIAutomationManager()
    backend = BackendFactory.create_backend('windows')
    session = AutomationSession(backend)
    
    # Запуск приложения
    app = Application.launch("test_app.exe")
    
    # Настройка OCR
    session.ocr.set_languages(['en', 'ru'])
    session.ocr.set_confidence_threshold(0.8)
    
    try:
        # Поиск и взаимодействие с элементами
        login_button = session.find_element_by_object_name("login_button")
        login_button.click()
        
        # Ожидание появления формы входа
        session.wait_until(lambda: session.ocr.verify_text_presence(
            element=None, text="Login Form"
        ))
        
        # Заполнение полей
        username_field = session.find_element_by_object_name("username")
        password_field = session.find_element_by_object_name("password")
        
        username_field.type_text("testuser")
        password_field.type_text("testpass")
        
        # Проверка введенных данных с помощью OCR
        entered_username = session.ocr.read_text_from_element(username_field)
        entered_password = session.ocr.read_text_from_element(password_field)
        
        print(f"Введенное имя пользователя: {entered_username}")
        print(f"Введенный пароль: {entered_password}")
        
        # Нажатие кнопки входа
        submit_button = session.find_element_by_object_name("submit")
        submit_button.click()
        
        # Проверка успешного входа
        success_text = session.ocr.verify_text_presence(
            element=None, text="Welcome"
        )
        
        if success_text:
            print("✅ Вход выполнен успешно!")
        else:
            print("❌ Ошибка входа")
            
    finally:
        # Завершение
        app.terminate()

if __name__ == "__main__":
    automate_with_ocr()
```

Это руководство поможет вам эффективно использовать OCR возможности PyUI Automation для создания интеллектуальных автоматизационных решений. 