# Arena Strike v1.3

A browser-based 3D first-person arena shooter built with Three.js. Fight an armored AI hostile across multiple environments with a full tactical HUD.

## Features

- **4 battlefields** — City, Jungle, Mountains, and Desert with unique scenery
- **Surrounding landscapes** — skylines, forests, peaks, and dunes visible beyond the arena
- **3D arena** with themed cover, walls, lighting, and fog per map
- **Detailed enemy** — armored combatant with glowing visor and rifle
- **Tactical HUD** — health, ammo, reload, threat level, minimap, hit marker
- **Two difficulties** — Normal and Hard
- **Pause menu** and post-match combat stats

## Battlefields

| Map | Surroundings | Arena feel |
|-----|--------------|------------|
| **City** | Neon skyline, lit windows | Concrete grid, neon trim |
| **Jungle** | Dense trees, undergrowth | Palm cover, green fog |
| **Mountains** | Snow peaks, pine forest | Rocky boulders, alpine sky |
| **Desert** | Sand dunes, cacti | Sandy floor, warm sunset |

## Controls

| Key | Action |
|-----|--------|
| ↑ ↓ ← → | Move & turn |
| Space | Shoot |
| R | Reload |
| P / Esc | Pause |

## Run locally

```bash
python -m http.server 3456 --directory .
```

Open `http://localhost:3456` in Chrome, Edge, or Firefox.

## Files

| File | Purpose |
|------|---------|
| `index.html` | Page structure, HUD, menus |
| `style.css` | HUD and menu styling |
| `game.js` | Game logic, AI, combat |
| `environments.js` | Map themes and surrounding scenery |
| `README.md` | Documentation |

## Tech

- [Three.js](https://threejs.org/) via CDN — no build step required
