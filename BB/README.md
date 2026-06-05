# Arena Strike v1.2

A browser-based 3D first-person arena shooter built with Three.js. Fight an armored AI hostile in a neon-lit arena with a full tactical HUD.

## Features

- **3D arena** with cover pillars, shadows, and neon lighting
- **Detailed enemy** — armored combatant with glowing visor, rifle, and insignia
- **Tactical HUD** — health, ammo, reload bar, threat level, minimap, crosshair, hit marker
- **Combat feedback** — damage vignette, off-screen enemy pointer, line-of-sight indicator
- **Two difficulties** — Normal and Hard (elite AI with burst fire and cover-seeking)
- **Pause menu** — resume or return to main menu
- **Post-match stats** — time, accuracy, hits, damage taken

## Controls

| Key | Action |
|-----|--------|
| ↑ | Move forward |
| ↓ | Move backward |
| ← | Turn left |
| → | Turn right |
| Space | Shoot |
| R | Reload |
| P / Esc | Pause |

## Difficulty

| | Normal | Hard |
|---|--------|------|
| Your HP | 100 | 80 |
| Enemy HP | 100 | 130 |
| Enemy damage | 18 | 24 |
| AI | Moderate | Fast, accurate, uses cover |

## Run locally

Serve the folder with any static file server:

```bash
python -m http.server 3456 --directory .
```

Then open `http://localhost:3456` in Chrome, Edge, or Firefox.

## Files

| File | Purpose |
|------|---------|
| `index.html` | Page structure, HUD, menus |
| `style.css` | HUD styling and overlays |
| `game.js` | Three.js game logic, AI, combat |
| `README.md` | Documentation |

## Tech

- [Three.js](https://threejs.org/) via CDN
- No build step — ES modules only
