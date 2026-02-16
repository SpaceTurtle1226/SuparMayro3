# Mario-like Platformer

A 2D side-scrolling platformer game built with Python and pygame, inspired by Super Mario Bros. 3.

## Features

- **3 Levels** with increasing difficulty
- **Procedural Generation** - Each playthrough creates a unique level layout
- **Enemies** - Goombas and Koopas with AI movement
- **Collectibles** - Coins scattered throughout levels
- **Synthesized Sound Effects** - Jump, coin, stomp, death, win sounds
- **Game States** - Pause, Game Over, Level Complete, Victory
- **No External Assets** - All graphics and audio generated programmatically

## Controls

| Key | Action |
|-----|--------|
| Arrow Keys / A,D | Move left/right |
| Space / W | Jump |
| P | Pause game |
| R | Restart (after game over/win) |

## Objective

- Collect coins (+100 points)
- Defeat enemies by jumping on them (+200 points)
- Reach the flag at the end of each level (+1000 points)
- Avoid spikes and pits
- Complete all 3 levels to win!

## Installation

```bash
pip install pygame
```

## Running the Game

```bash
python mario_platformer.py
```

## Level Design

The game generates random levels with:

- Ground platforms with pits to jump over
- Pipes (various heights)
- Floating brick platforms
- Spikes as hazards
- Coins and enemies placed strategically

### Level Progression

| Level | Width | Features |
|-------|-------|----------|
| 1 | 60 tiles | Basic obstacles, Goombas |
| 2 | 80 tiles | Taller pipes, mixed enemies |
| 3 | 100 tiles | Maximum challenge |

## Game Mechanics

- **Player**: Red character with jump and run animations
- **Goomba**: Brown enemy, moves back and forth
- **Koopa**: Green enemy, faster movement
- **Stomp enemies** from above to defeat them
- **3 lives** per game

## Requirements

- Python 3.x
- pygame

## License

MIT
