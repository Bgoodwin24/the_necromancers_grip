# The Necromancer's Grip

## Project Overview
This is a sidescrolling fighting game made with Pygame where you play as a rogue traveling through a graveyard to fight the necromancer that has taken up residence in the mausoleum.

## Motivation
This project is a love letter to the pixel art games I grew up with — simple controls, expressive sprites, and nostalgic charm. As a developer and artist, I wanted to combine my passion for video games and visual storytelling into a playable experience. This was my first video game project, and I challenged myself to design all the animations and visuals by hand, drawing from classic sidescrollers for inspiration. The result is a game that reflects both technical growth and personal creativity.

## Features:
- Fully hand-drawn pixel art, including backgrounds, characters, and effects
- Two unique enemy types with behavior and animations
- One collectible item (health potion)
- Character animations: idle, run, attack, damage, and death
- Responsive controls for fluid gameplay
- Clean separation of gameplay logic and rendering using Pygame
- **No audio** included due to the lack of a digital audio workstation (DAW)

## Controls:
- A = Move Left
- D = Move Right
- Space = Attack

## Game Showcase:
![Game Showcase](https://github.com/Bgoodwin24/the_necromancers_grip/raw/main/Images/PNGs/NecromancersGrip.gif)

## Dependencies
### 
- Python (v3.10.12 or later)
- Pygame library installed

## Quick Start
1. Clone the repository:
```bash
   git clone https://github.com/Bgoodwin24/the_necromancers_grip.git
```

2. Navigate to the project directory:
```bash
    cd the_necromancers_grip
```

3. Run the game:
```bash
    python main.py
```

## Setup Instructions
1. Install Python 3.10.12
On Ubuntu / Debian:
```bash
sudo apt update
sudo apt install -y python3.10 python3.10-venv python3.10-dev
```
On macOS (via Homebrew):
```bash
brew update
brew install python@3.10
```
Then add Python 3.10 to your path (optional depending on shell):

```bash
echo 'export PATH="/opt/homebrew/opt/python@3.10/bin:$PATH"' >> ~/.zprofile
source ~/.zprofile
```

2. Create a virtual environment (recommended)
```bash
python3.10 -m venv venv
source venv/bin/activate
```
3. Upgrade pip
```bash
python -m pip install --upgrade pip
```
4. Install Pygame
```bash
pip install pygame
```

## License

This project is licensed under the [Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)](https://creativecommons.org/licenses/by-nc/4.0/).

You are free to:

- **Share** — copy and redistribute the material in any medium or format.
- **Adapt** — remix, transform, and build upon the material.

Under the following terms:

- **Attribution** — You must give appropriate credit, provide a link to the license, and indicate if changes were made.
- **NonCommercial** — You may not use the material for commercial purposes.

No additional restrictions — You may not apply legal terms or technological measures that legally restrict others from doing anything the license permits.

See the full license in the [LICENSE](LICENSE) file.

## Contributing

I would love your help! If you have any ideas or improvements, contribute by forking the repo and opening a pull request to the `main` branch. **Please be sure to write tests for any changes if applicable.**

## Author
Bgoodwin24
