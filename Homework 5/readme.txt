Maze Game - Amir Nazemi
=======================================

SETUP INSTRUCTIONS:
-------------------
1. Ensure you have Python 3.x installed
2. Install required packages:
   pip install pygame PyOpenGL PyOpenGL_accelerate

3. Unpack Homework 5 folder
4. Run the game:
   python maze_game.py


GAME OBJECTIVE:
---------------
Navigate through the randomly generated maze from the starting position (0,0)
to the goal at the opposite corner. The game tracks your time and position.


CONTROLS:
---------
W/A/S/D     - Move forward/left/backward/right
Mouse       - Look around
H           - Toggle help screen
1           - Use wall breaker (when you have one)
3           - Drop glow stick marker (3 total available)
T           - Teleport (when standing on purple teleport pad)
R           - Reset to start position
N           - Generate new maze
ESC         - Exit game


GAME ELEMENTS:
--------------

POWER-UPS (collect to use):
  • Orange Cube    - Wall Breaker: Break one wall you're facing (press 1)
  • Cyan Torus     - Shield: Blocks the next trap you encounter

TRAPS (single use, touch to trigger):
  • Red Sphere     - Reset: Sends you back to start
  • Gray Sphere    - Dark Zone: Limits vision for 15 seconds
  • Pink Sphere    - Invert: Inverts controls for 15 seconds

OTHER:
  • Green Sphere   - Goal: Reach this to win!
  • Purple Disc    - Teleport Pad: Press T to teleport to random location
  • Yellow Marker  - Your Glow Stick: Marks where you've been


NOTES:
------
- The shield will block the next trap and then disappear
- Each trap can only trigger once
- Teleport pads are reusable - you can use them multiple times
- Glow sticks provide light and mark your path (3 maximum)
- Wall breaker cannot break outer maze walls
- Timer continues running even if you hit reset traps
- Press H anytime during the game for controls reminder


TEXTURES + MAZE GENERATION:
---------
This game uses the following texture packs (included in textures folder):
- Brick pavement for floor
- Rough plaster for walls

If textures fail to load, the game will continue with colored surfaces.

