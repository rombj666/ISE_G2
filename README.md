# Moonbound Eclipse Trial

Moonbound Eclipse Trial is a 2D Pygame action platformer prototype.

Current setup includes:
- Pygame project structure
- Settings file
- Larger map flow with camera scrolling
- Asset folders
- Documentation folder
- Working game window

## Project Structure

```text
src/
|-- __init__.py
|-- core/
|   |-- __init__.py
|   |-- camera.py
|   |-- game_state.py
|   `-- input_handler.py
|-- entities/
|   |-- __init__.py
|   |-- player.py
|   `-- enemy.py
|-- systems/
|   |-- __init__.py
|   |-- combat.py
|   |-- weapons.py
|   |-- skills.py
|   |-- projectile.py
|   |-- coin.py
|   |-- shop.py
|   `-- effects.py
|-- levels/
|   |-- __init__.py
|   |-- game_map.py
|   |-- room.py
|   |-- level.py
|   `-- level_manager.py
|-- ui/
|   |-- __init__.py
|   `-- ui.py
`-- audio/
    |-- __init__.py
    `-- audio.py
```
