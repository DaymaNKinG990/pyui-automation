# UI Elements

Этот гайд описывает все поддерживаемые PyUI Automation UI-элементы и работу с ними.

## Основные элементы

### Button
```python
el = session.find_element_by_object_name("submitBtn")
el.click()
if el.is_enabled():
    el.click()
```

### Input Field
```python
input_field = session.find_element_by_object_name("username")
input_field.type_text("user123")
input_field.clear()
value = input_field.get_text()
```

### Checkbox
```python
checkbox = session.find_element_by_object_name("agree")
if not checkbox.is_checked():
    checkbox.click()
checkbox.toggle()
```

### Radio Button
```python
radio = session.find_element_by_object_name("option1")
radio.click()
if radio.is_selected():
    ...
```

### Dropdown/Combobox
```python
dropdown = session.find_element_by_object_name("country")
dropdown.select_option("United States")
dropdown.select_index(0)
options = dropdown.get_options()
selected = dropdown.get_selected_option()
```

### Window
```python
window = session.find_element_by_object_name("Main Window")
window.maximize()
window.minimize()
window.restore()
window.close()
size = window.size
position = window.location
```

### Tab
```python
tab_control = session.find_element_by_object_name("SettingsTab")
tab_control.select_tab("General")
active_tab = tab_control.get_active_tab()
tabs = tab_control.get_tabs()
```

### Menu
```python
menu = session.find_element_by_object_name("FileMenu")
menu.click()
# Для сложных меню используйте последовательный поиск и click
```

### TreeView
```python
tree = session.find_element_by_object_name("file-tree")
tree.expand_node("Documents")
tree.select_node("Documents/Reports")
selected = tree.get_selected_node()
```

## Пример: работа с элементами Notepad++
```python
app = Application.launch(r"D:/Programs/Notepad++/notepad++.exe")
window = app.wait_for_window("Notepad++")
session = AutomationSession(backend)
main = session.find_element_by_object_name("Notepad++")
main.type_text("Hello, world!")
# Поиск кнопки "Сохранить" и клик
save_btn = session.find_element_by_object_name("Save")
save_btn.click()
```

## Свойства элементов
```python
el = session.find_element_by_object_name("submitBtn")
name = el.name
class_name = el.class_name
enabled = el.is_enabled()
visible = el.is_visible()
location = el.location
size = el.size
```

## Действия с элементами
```python
el.click()
el.double_click()
el.right_click()
el.type_text("Hello World")
el.clear()
el.hover()
```

## Поиск элементов
```python
el = session.find_element_by_object_name("mainButton")
els = session.find_elements_by_widget_type("QPushButton")
el2 = session.find_element_by_text("OK")
```

## Best Practices
- Используйте только поддерживаемые методы поиска (objectName, widget, text, property).
- Для сложных элементов комбинируйте поиск по разным стратегиям.
- Для Notepad++ и других приложений всегда проверяйте корректность objectName.
- Для визуального тестирования используйте capture_screenshot и сравнение baseline.
