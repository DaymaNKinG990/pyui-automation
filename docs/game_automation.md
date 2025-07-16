# Game UI Automation Guide

Этот гайд описывает использование PyUI Automation для тестирования и автоматизации игровых UI, с акцентом на работу с элементами и интеграцию с core API.

## Основы

```python
from pyui_automation.core import AutomationSession
from pyui_automation.core.factory import BackendFactory
from pyui_automation.game_elements import (
    HealthBar, SkillBar, WorldMap, InventorySlot
)

backend = BackendFactory.create_backend('windows')
session = AutomationSession(backend)

# Инициализация игровых UI-элементов
health_bar = HealthBar(session)
skill_bar = SkillBar(session)
world_map = WorldMap(session)
inventory = InventorySlot(session)
```

## Примеры сценариев

### Мониторинг здоровья
```python
current_health = health_bar.current_value
max_health = health_bar.max_value
if health_bar.is_low():
    # Использовать зелье
    ...
```

### Использование скиллов
```python
if not skill_bar.is_on_cooldown(1):
    skill_bar.use_skill(1)
```

### Работа с инвентарём
```python
slot = inventory.get_slot(1, 1)
if slot.is_empty():
    slot.place_item()
else:
    item = slot.get_item()
    print(f"Found {item.name}")
```

### Работа с картой
```python
pos = world_map.get_player_position()
world_map.set_waypoint(x=100, y=200)
if world_map.is_in_area("Safe Zone"):
    print("Player is in safe zone")
```

### Социальные функции
```python
party = session.find_element_by_object_name("party_frame")
for member in party.get_children():
    if member.health_percentage < 50:
        # Лечим участника
        ...
```

## Визуальное сравнение игровых элементов
```python
session.init_visual_testing("visual_baseline/")
session.capture_visual_baseline("health_bar")
result = session.compare_visual("health_bar")
if not result["match"]:
    session.generate_visual_report("health_bar", result["differences"], "reports/")
```

## Best Practices
- Для игровых UI используйте специализированные классы из game_elements.
- Для сложных сценариев комбинируйте визуальное сравнение и работу с координатами.
- Для автоматизации действий используйте session.mouse и session.keyboard.
- Для мониторинга состояния используйте свойства игровых элементов.
- Для интеграции с core API всегда используйте AutomationSession и backend.
