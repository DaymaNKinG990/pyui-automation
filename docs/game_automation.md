# Game UI Automation Guide

This guide covers how to use PyUI Automation for game testing and automation, with a focus on UI elements and game-specific features.

## Table of Contents
- [Basic Setup](#basic-setup)
- [Game UI Elements](#game-ui-elements)
  - [Health & Resource Bars](#health--resource-bars)
  - [Skill & Action Bars](#skill--action-bars)
  - [Inventory & Equipment](#inventory--equipment)
  - [Maps & Navigation](#maps--navigation)
  - [Social & Party Systems](#social--party-systems)
  - [Quest & Achievement Tracking](#quest--achievement-tracking)
- [Advanced Topics](#advanced-topics)

## Basic Setup

```python
from pyui_automation import Session
from pyui_automation.game_elements import (
    HealthBar, 
    SkillBar,
    WorldMap,
    InventorySlot
)

# Create automation session
session = Session()

# Initialize game UI elements
health_bar = HealthBar(session)
skill_bar = SkillBar(session)
world_map = WorldMap(session)
inventory = InventorySlot(session)
```

## Game UI Elements

### Health & Resource Bars

Monitor and interact with health, mana, and other resource bars:

```python
# Health bar interactions
current_health = health_bar.current_value
max_health = health_bar.max_value
health_percent = health_bar.percentage

# Check health status
if health_bar.is_low():
    use_health_potion()
```

### Skill & Action Bars

Manage skills, spells, and abilities:

```python
# Use skills
skill_bar.use_skill(1)  # Use first skill
skill_bar.use_skill_by_name("Fireball")

# Check cooldowns
if not skill_bar.is_on_cooldown(2):
    skill_bar.use_skill(2)
```

### Inventory & Equipment

Handle inventory management and equipment:

```python
# Inventory operations
slot = inventory.get_slot(1, 1)
if slot.is_empty():
    slot.place_item()
else:
    item = slot.get_item()
    print(f"Found {item.name}")

# Equipment management
equipment.equip_item("Sword")
equipment.unequip_slot("MainHand")
```

### Maps & Navigation

Work with world maps and navigation:

```python
# Map interactions
current_pos = world_map.get_player_position()
world_map.set_waypoint(x=100, y=200)
world_map.zoom(level=2)

# Area detection
if world_map.is_in_area("Safe Zone"):
    print("Player is in safe zone")
```

### Social & Party Systems

Manage social interactions and party mechanics:

```python
# Party management
party = party_frame.get_party_members()
for member in party:
    if member.health_percentage < 50:
        heal_party_member(member)

# Social features
friends = social_panel.get_friends_list()
social_panel.send_message("Hello!", target="Friend")
```

### Quest & Achievement Tracking

Track quests and achievements:

```python
# Quest tracking
active_quests = quest_log.get_active_quests()
for quest in active_quests:
    if quest.is_complete():
        quest.turn_in()

# Achievement progress
achievements = achievement_panel.get_achievements()
for achievement in achievements:
    print(f"{achievement.name}: {achievement.progress}%")
```

## Advanced Topics

### Error Handling

```python
try:
    skill_bar.use_skill(1)
except ElementNotFoundError:
    print("Skill bar not visible")
except CooldownError:
    print("Skill is on cooldown")
```

### Performance Optimization

```python
# Enable performance monitoring
with session.measure_performance() as perf:
    skill_bar.use_skill(1)
    world_map.set_waypoint(x=100, y=200)
    
print(f"Actions took: {perf.duration}ms")
```

### Visual Verification

```python
# Verify UI element state
if health_bar.verify_visual_state():
    print("Health bar displayed correctly")

# Compare with reference image
if world_map.compare_with_reference("map_state.png", threshold=0.95):
    print("Map state matches reference")
```

## Best Practices

1. Always handle errors and edge cases
2. Use visual verification for critical UI elements
3. Monitor performance metrics
4. Implement cooldown and rate limiting
5. Add randomization to prevent detection
6. Keep logs for debugging

## Next Steps

- Explore [API Reference](./api_reference.md) for detailed documentation
- Check [Advanced Topics](./advanced_topics.md) for more features
- Read [Core Concepts](./core_concepts.md) for architecture details
