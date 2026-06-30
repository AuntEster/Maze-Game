"""
Maze Game
"""

import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import math
import random

# Import maze generator
from maze_generator import Maze

def load_texture(filename):
    """Load a texture file and return OpenGL texture ID"""
    try:
        texture_surface = pygame.image.load(filename)
        texture_data = pygame.image.tostring(texture_surface, "RGBA", 1)
        width = texture_surface.get_width()
        height = texture_surface.get_height()
        
        glEnable(GL_TEXTURE_2D)
        texid = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texid)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height,
                     0, GL_RGBA, GL_UNSIGNED_BYTE, texture_data)
        
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        
        return texid
    except Exception as e:
        print(f"Failed to load texture {filename}: {e}")
        return None

def get_safe_random_pos(maze, exclude_positions=[]):
    """Get a safe random position for power-up placement with bounds checking"""
    if maze.rows > 4 and maze.cols > 4:
        r = random.randint(2, maze.rows - 3)
        c = random.randint(2, maze.cols - 3)
    else:
        r = random.randint(1, max(1, maze.rows - 2))
        c = random.randint(1, max(1, maze.cols - 2))
    
    # Avoid start position and excluded positions
    while (r == 0 and c == 0) or (r, c) in exclude_positions:
        if maze.rows > 4 and maze.cols > 4:
            r = random.randint(2, maze.rows - 3)
            c = random.randint(2, maze.cols - 3)
        else:
            r = random.randint(1, max(1, maze.rows - 2))
            c = random.randint(1, max(1, maze.cols - 2))
    
    return r, c


def check_wall_collision(maze, pos_x, pos_y, cell_size, player_radius=0.3):
    """
    Check if position (pos_x, pos_y) collides with walls
    Returns True if collision (blocked), False if clear
    """
    # Which cell are we in?
    cell_c = int(pos_x / cell_size)
    cell_r = int(pos_y / cell_size)
    
    # Bounds check
    if cell_c < 0 or cell_c >= maze.cols or cell_r < 0 or cell_r >= maze.rows:
        return True
    
    # Position within cell (0 to cell_size)
    local_x = pos_x - (cell_c * cell_size)
    local_y = pos_y - (cell_r * cell_size)
    
    idx = maze.index(cell_r, cell_c)
    cell = maze.grid[idx]
    
    # Check each wall: North=0, East=1, South=2, West=3
    # North wall (local_y near 0)
    if cell.wall[0] and local_y < player_radius:
        return True
    
    # South wall (local_y near cell_size)
    if cell.wall[2] and local_y > cell_size - player_radius:
        return True
    
    # West wall (local_x near 0)
    if cell.wall[3] and local_x < player_radius:
        return True
    
    # East wall (local_x near cell_size)
    if cell.wall[1] and local_x > cell_size - player_radius:
        return True
    
    return False


def draw_maze_walls(maze, cell_size=2.0, wall_height=2.0, wall_texture=None):
    """Draw the 3D maze walls"""
    if wall_texture:
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, wall_texture)
        glColor3f(1, 1, 1)  # White to show texture properly
    else:
        glColor3f(0.7, 0.7, 0.7)
    
    for r in range(maze.rows):
        for c in range(maze.cols):
            idx = maze.index(r, c)
            cell = maze.grid[idx]
            
            x = c * cell_size
            y = r * cell_size
            z = 0
            
            # North wall
            if cell.wall[0]:
                glBegin(GL_QUADS)
                glTexCoord2f(0,0);glVertex3f(x, y, z)
                glTexCoord2f(cell_size,0);glVertex3f(x + cell_size, y, z)
                glTexCoord2f(cell_size,wall_height);glVertex3f(x + cell_size, y, z + wall_height)
                glTexCoord2f(0,wall_height);glVertex3f(x, y, z + wall_height)
                glEnd()
            
            # East wall
            if cell.wall[1]:
                glBegin(GL_QUADS)
                glTexCoord2f(0,0);glVertex3f(x + cell_size, y, z)
                glTexCoord2f(0,cell_size);glVertex3f(x + cell_size, y + cell_size, z)
                glTexCoord2f(wall_height,cell_size);glVertex3f(x + cell_size, y + cell_size, z + wall_height)
                glTexCoord2f(wall_height,0);glVertex3f(x + cell_size, y, z + wall_height)
                glEnd()
            
            # South wall
            if cell.wall[2]:
                glBegin(GL_QUADS)
                glTexCoord2f(0,0);glVertex3f(x, y + cell_size, z)
                glTexCoord2f(cell_size,0);glVertex3f(x + cell_size, y + cell_size, z)
                glTexCoord2f(cell_size,wall_height);glVertex3f(x + cell_size, y + cell_size, z + wall_height)
                glTexCoord2f(0,wall_height);glVertex3f(x, y + cell_size, z + wall_height)
                glEnd()
            
            # West wall
            if cell.wall[3]:
                glBegin(GL_QUADS)
                glTexCoord2f(0,0);glVertex3f(x, y, z)
                glTexCoord2f(0,cell_size);glVertex3f(x, y + cell_size, z)
                glTexCoord2f(wall_height,cell_size);glVertex3f(x, y + cell_size, z + wall_height)
                glTexCoord2f(wall_height,0);glVertex3f(x, y, z + wall_height)
                glEnd()
                
    if wall_texture:
        glDisable(GL_TEXTURE_2D)


def draw_floor_ceiling(maze, cell_size=2.0, wall_height=2.0, floor_texture=None):
    """Draw floor and ceiling"""
    maze_width = maze.cols * cell_size
    maze_depth = maze.rows * cell_size
    
    # Floor
    if floor_texture:
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, floor_texture)
        glColor3f(1, 1, 1)
    else:
        glColor3f(0.3, 0.3, 0.3)
    
    glColor3f(0.3, 0.3, 0.3)
    glBegin(GL_QUADS)
    glTexCoord2f(0,0);glVertex3f(0, 0, 0)
    glTexCoord2f(maze.cols,0);glVertex3f(maze_width, 0, 0)
    glTexCoord2f(maze.cols,maze.rows);glVertex3f(maze_width, maze_depth, 0)
    glTexCoord2f(0,maze.rows);glVertex3f(0, maze_depth, 0)
    glEnd()
    
    if floor_texture:
        glDisable(GL_TEXTURE_2D)
    
    # Ceiling
    glColor3f(0.2, 0.2, 0.2)
    glBegin(GL_QUADS)
    glVertex3f(0, 0, wall_height)
    glVertex3f(maze_width, 0, wall_height)
    glVertex3f(maze_width, maze_depth, wall_height)
    glVertex3f(0, maze_depth, wall_height)
    glEnd()


def draw_goal_marker(maze, cell_size=2.0):
    """Draw goal marker"""
    goal_r = maze.rows - 1
    goal_c = maze.cols - 1
    
    x = goal_c * cell_size + cell_size / 2
    y = goal_r * cell_size + cell_size / 2
    z = 1.0
    
    glPushMatrix()
    glTranslatef(x, y, z)
    
    # add glowing effect
    glMaterialfv(GL_FRONT_AND_BACK, GL_EMISSION, [0.0, 5.0, 0.0, 1.0])
    glColor3f(0.0, 1.0, 0.0)
    sphere = gluNewQuadric()
    gluSphere(sphere, 0.3, 16, 16)
    
    # reset emission
    glMaterialfv(GL_FRONT_AND_BACK, GL_EMISSION, [0.0, 0.0, 0.0, 1.0])
    glPopMatrix()
    

def draw_traps(traps, cell_size=2.0):
    """Draw reset trap markers"""
    for trap_r, trap_c in traps:
        x = trap_c * cell_size + cell_size / 2
        y = trap_r * cell_size + cell_size / 2
        z = 0.5  # Lower to ground
        
        glPushMatrix()
        glTranslatef(x, y, z)
        glColor3f(1.0, 0.0, 0.0)  # Red
        sphere = gluNewQuadric()
        gluSphere(sphere, 0.2, 16, 16)
        glPopMatrix()


def draw_dark_traps(traps, cell_size=2.0):
    """Draw dark zone trap markers"""
    for trap_r, trap_c in traps:
        x = trap_c * cell_size + cell_size / 2
        y = trap_r * cell_size + cell_size / 2
        z = 0.5
        
        glPushMatrix()
        glTranslatef(x, y, z)
        glColor3f(0.2, 0.2, 0.2)  # Dark gray
        sphere = gluNewQuadric()
        gluSphere(sphere, 0.2, 16, 16)
        glPopMatrix()


def draw_invert_traps(traps, cell_size=2.0):
    """Draw invert controls trap markers"""
    for trap_r, trap_c in traps:
        x = trap_c * cell_size + cell_size / 2
        y = trap_r * cell_size + cell_size / 2
        z = 0.5
        
        glPushMatrix()
        glTranslatef(x, y, z)
        glColor3f(1.0, 0.5, 1.0)  # Pink
        sphere = gluNewQuadric()
        gluSphere(sphere, 0.2, 16, 16)
        glPopMatrix()


def draw_shield(shield_pos, cell_size=2.0):
    """Draw shield power-up as a rotating torus"""
    if shield_pos is None:
        return
    
    sh_r, sh_c = shield_pos
    x = sh_c * cell_size + cell_size / 2
    y = sh_r * cell_size + cell_size / 2
    z = 1.0
    
    glPushMatrix()
    glTranslatef(x, y, z)
    glColor3f(0.0, 0.5, 1.0)  # Cyan/blue
    
    import time
    angle = (time.time() * 50) % 360
    glRotatef(angle, 0, 0, 1)
    
    # Draw torus (shield shape)
    from OpenGL.GLUT import glutSolidTorus
    try:
        glutSolidTorus(0.05, 0.2, 8, 16)
    except:
        # Fallback to sphere if GLUT not available
        sphere = gluNewQuadric()
        gluSphere(sphere, 0.2, 16, 16)
    
    glPopMatrix()


def draw_glow_sticks(glow_sticks):
    """Draw glow stick markers - small cylinders on floor pointing in camera direction"""
    for gx, gy, gz, gyaw in glow_sticks:
        glPushMatrix()
        
        # Position on floor
        glTranslatef(gx, gy, 0.05)  # Slightly above floor
        
        # Rotate to match the direction the player was facing when placed
        glRotatef(gyaw - 90, 0, 0, 1)  # Rotate in XY plane to match yaw direction
        
        # Draw as a small glowing cylinder lying on the floor
        # Use emission to make it glow (not just reflect light)
        glMaterialfv(GL_FRONT_AND_BACK, GL_EMISSION, [6.0, 6.0, 0.0, 1.0])
        glColor3f(1.0, 1.0, 0.0)  # Yellow/gold glow
        cylinder = gluNewQuadric()
        glRotatef(90, 0, 1, 0)  # Lay it flat (along X axis after yaw rotation)
        gluCylinder(cylinder, 0.02, 0.02, 0.3, 8, 8)  # radius=0.02, length=0.3
        
        # Reset emission
        glMaterialfv(GL_FRONT_AND_BACK, GL_EMISSION, [0.0, 0.0, 0.0, 1.0])
        
        glPopMatrix()


def draw_teleport_pads(teleport_pads, cell_size=2.0):
    """Draw teleport pads as flat discs on the floor"""
    for tp_r, tp_c in teleport_pads:
        x = tp_c * cell_size + cell_size / 2
        y = tp_r * cell_size + cell_size / 2
        z = 0.01  # Just above floor
        
        glPushMatrix()
        glTranslatef(x, y, z)
        glColor3f(0.5, 0.0, 1.0)  # Purple/magenta
        
        # Draw a flat disc
        disc = gluNewQuadric()
        glRotatef(90, 0, 0, 1)  # Make it horizontal
        gluDisk(disc, 0, 0.4, 16, 1)  # radius=0.4
        
        glPopMatrix()


def draw_wall_breaker(wall_breaker_pos, cell_size=2.0):
    """Draw wall breaker power-up as a floating cube"""
    if wall_breaker_pos is None:
        return
    
    wb_r, wb_c = wall_breaker_pos
    x = wb_c * cell_size + cell_size / 2
    y = wb_r * cell_size + cell_size / 2
    z = 1.0  # Floating height
    
    glPushMatrix()
    glTranslatef(x, y, z)
    glColor3f(1.0, 0.5, 0.0)  # Orange
    
    # Draw a small rotating cube
    import time
    angle = (time.time() * 50) % 360
    glRotatef(angle, 0, 0, 1)
    glRotatef(angle * 0.7, 1, 0, 0)
    
    # Draw cube
    size = 0.2
    glBegin(GL_QUADS)
    # Front
    glVertex3f(-size, -size, size)
    glVertex3f(size, -size, size)
    glVertex3f(size, size, size)
    glVertex3f(-size, size, size)
    # Back
    glVertex3f(-size, -size, -size)
    glVertex3f(-size, size, -size)
    glVertex3f(size, size, -size)
    glVertex3f(size, -size, -size)
    # Top
    glVertex3f(-size, size, -size)
    glVertex3f(-size, size, size)
    glVertex3f(size, size, size)
    glVertex3f(size, size, -size)
    # Bottom
    glVertex3f(-size, -size, -size)
    glVertex3f(size, -size, -size)
    glVertex3f(size, -size, size)
    glVertex3f(-size, -size, size)
    # Right
    glVertex3f(size, -size, -size)
    glVertex3f(size, size, -size)
    glVertex3f(size, size, size)
    glVertex3f(size, -size, size)
    # Left
    glVertex3f(-size, -size, -size)
    glVertex3f(-size, -size, size)
    glVertex3f(-size, size, size)
    glVertex3f(-size, size, -size)
    glEnd()
    
    glPopMatrix()


def draw_hud(font, elapsed_time, player_x, player_y, cell_size, has_won=False, win_time=0, glow_sticks_remaining=0, teleport_prompt=False, has_wall_breaker=False, has_shield=False, dark_zone_active=False, invert_active=False):
    """Draw HUD with timer and position"""
    # Calculate current cell
    cell_c = int(player_x / cell_size)
    cell_r = int(player_y / cell_size)
    
    # Format time (mm:ss.ms)
    if has_won:
        seconds = win_time / 1000.0
    else:
        seconds = elapsed_time / 1000.0
    minutes = int(seconds / 60)
    secs = seconds % 60
    time_str = f"Time: {minutes:02d}:{secs:05.2f}"
    pos_str = f"Position: ({cell_c}, {cell_r})"
    glow_str = f"Glow Sticks: {glow_sticks_remaining}"
    wall_str = f"Wall Breaker: {'YES' if has_wall_breaker else 'NO'}"
    shield_str = f"Shield: {'YES' if has_shield else 'NO'}"
    
    # Render text to surface
    time_surface = font.render(time_str, True, (255, 255, 255), (0, 0, 0))
    pos_surface = font.render(pos_str, True, (255, 255, 255), (0, 0, 0))
    glow_surface = font.render(glow_str, True, (255, 255, 0), (0, 0, 0))
    wall_surface = font.render(wall_str, True, (255, 128, 0) if has_wall_breaker else (128, 128, 128), (0, 0, 0))
    shield_surface = font.render(shield_str, True, (0, 128, 255) if has_shield else (128, 128, 128), (0, 0, 0))
    
    # Convert to OpenGL texture data
    time_data = pygame.image.tostring(time_surface, "RGBA", True)
    pos_data = pygame.image.tostring(pos_surface, "RGBA", True)
    glow_data = pygame.image.tostring(glow_surface, "RGBA", True)
    wall_data = pygame.image.tostring(wall_surface, "RGBA", True)
    shield_data = pygame.image.tostring(shield_surface, "RGBA", True)
    
    # Draw at screen position
    glWindowPos2d(10, 10)
    glDrawPixels(time_surface.get_width(), time_surface.get_height(), 
                 GL_RGBA, GL_UNSIGNED_BYTE, time_data)
    
    glWindowPos2d(10, 40)
    glDrawPixels(pos_surface.get_width(), pos_surface.get_height(), 
                 GL_RGBA, GL_UNSIGNED_BYTE, pos_data)
    
    glWindowPos2d(10, 70)
    glDrawPixels(glow_surface.get_width(), glow_surface.get_height(), 
                 GL_RGBA, GL_UNSIGNED_BYTE, glow_data)
    
    glWindowPos2d(10, 100)
    glDrawPixels(wall_surface.get_width(), wall_surface.get_height(), 
                 GL_RGBA, GL_UNSIGNED_BYTE, wall_data)
    
    glWindowPos2d(10, 130)
    glDrawPixels(shield_surface.get_width(), shield_surface.get_height(), 
                 GL_RGBA, GL_UNSIGNED_BYTE, shield_data)
    
    # Status effects
    if dark_zone_active:
        dark_font = pygame.font.SysFont('Arial', 28, bold=True)
        dark_surface = dark_font.render("DARK ZONE ACTIVE", True, (50, 50, 50), (0, 0, 0))
        dark_data = pygame.image.tostring(dark_surface, "RGBA", True)
        glWindowPos2d(300, 50)
        glDrawPixels(dark_surface.get_width(), dark_surface.get_height(), 
                     GL_RGBA, GL_UNSIGNED_BYTE, dark_data)
    
    if invert_active:
        inv_font = pygame.font.SysFont('Arial', 28, bold=True)
        inv_surface = inv_font.render("CONTROLS INVERTED", True, (255, 100, 255), (0, 0, 0))
        inv_data = pygame.image.tostring(inv_surface, "RGBA", True)
        glWindowPos2d(300, 100)
        glDrawPixels(inv_surface.get_width(), inv_surface.get_height(), 
                     GL_RGBA, GL_UNSIGNED_BYTE, inv_data)
    
    # Teleport prompt
    if teleport_prompt:
        tp_font = pygame.font.SysFont('Arial', 32, bold=True)
        tp_surface = tp_font.render("Press 'T' to TELEPORT", True, (200, 0, 255), (0, 0, 0))
        tp_data = pygame.image.tostring(tp_surface, "RGBA", True)
        glWindowPos2d(300, 500)
        glDrawPixels(tp_surface.get_width(), tp_surface.get_height(), 
                     GL_RGBA, GL_UNSIGNED_BYTE, tp_data)
    
    # Win message
    if has_won:
        win_font = pygame.font.SysFont('Arial', 48, bold=True)
        win_surface = win_font.render("YOU WIN!", True, (0, 255, 0), (0, 0, 0))
        win_data = pygame.image.tostring(win_surface, "RGBA", True)
        glWindowPos2d(400, 400)  # Center-ish
        glDrawPixels(win_surface.get_width(), win_surface.get_height(), 
                     GL_RGBA, GL_UNSIGNED_BYTE, win_data)



def draw_help_overlay(font):
    """Draw semi-transparent help overlay with controls and item descriptions"""
    # Draw semi-transparent black background
    # We'll use glBlendFunc for transparency
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glDisable(GL_DEPTH_TEST)
    glDisable(GL_LIGHTING)
    
    # Switch to 2D orthographic projection
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(0, 1000, 0, 800, -1, 1)  # Match display size
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    # Draw dark overlay
    glColor4f(0.0, 0.0, 0.0, 0.7)  # Black with 70% opacity
    glBegin(GL_QUADS)
    glVertex2f(0, 0)
    glVertex2f(1000, 0)
    glVertex2f(1000, 800)
    glVertex2f(0, 800)
    glEnd()
    
    # Restore matrices
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    
    glDisable(GL_BLEND)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    
    # Now draw text over the overlay
    title_font = pygame.font.SysFont('Arial', 36, bold=True)
    section_font = pygame.font.SysFont('Arial', 24, bold=True)
    text_font = pygame.font.SysFont('Arial', 20)
    
    y_pos = 750
    
    # Title
    title_surf = title_font.render("=== HELP / CONTROLS ===", True, (255, 255, 100), (0, 0, 0))
    title_data = pygame.image.tostring(title_surf, "RGBA", True)
    glWindowPos2d(300, y_pos)
    glDrawPixels(title_surf.get_width(), title_surf.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, title_data)
    y_pos -= 60
    
    # Controls section
    controls = [
        ("MOVEMENT:", None),
        ("  W/A/S/D", "Move forward/left/backward/right"),
        ("  Mouse", "Look around"),
        ("", None),
        ("ACTIONS:", None),
        ("  H", "Toggle this help screen"),
        ("  1", "Use wall breaker (break facing wall)"),
        ("  3", "Drop glow stick marker (3 max)"),
        ("  T", "Teleport (when on purple pad)"),
        ("  R", "Reset to start"),
        ("  N", "Generate new maze"),
        ("  ESC", "Exit game"),
    ]
    
    section_surf = section_font.render("CONTROLS:", True, (100, 200, 255), (0, 0, 0))
    section_data = pygame.image.tostring(section_surf, "RGBA", True)
    glWindowPos2d(50, y_pos)
    glDrawPixels(section_surf.get_width(), section_surf.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, section_data)
    y_pos -= 35
    
    for key, desc in controls:
        if desc is None:
            # Section header
            text_surf = text_font.render(key, True, (200, 200, 200), (0, 0, 0))
        else:
            text_surf = text_font.render(f"{key:12} - {desc}", True, (220, 220, 220), (0, 0, 0))
        text_data = pygame.image.tostring(text_surf, "RGBA", True)
        glWindowPos2d(60, y_pos)
        glDrawPixels(text_surf.get_width(), text_surf.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, text_data)
        y_pos -= 25
    
    # Items section
    y_pos = 750
    x_pos = 550
    
    section_surf = section_font.render("GAME ELEMENTS:", True, (100, 200, 255), (0, 0, 0))
    section_data = pygame.image.tostring(section_surf, "RGBA", True)
    glWindowPos2d(x_pos, y_pos)
    glDrawPixels(section_surf.get_width(), section_surf.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, section_data)
    y_pos -= 40
    
    items = [
        ("POWER-UPS (collect to use):", (255, 255, 150)),
        ("  Orange Cube - Wall Breaker", (255, 150, 50)),
        ("  Cyan Torus - Shield (blocks trap)", (100, 200, 255)),
        ("", (255, 255, 255)),
        ("TRAPS (single use):", (255, 150, 150)),
        ("  Red Sphere - Reset to start", (255, 100, 100)),
        ("  Gray Sphere - Dark zone (15s)", (150, 150, 150)),
        ("  Pink Sphere - Invert controls (15s)", (255, 150, 255)),
        ("", (255, 255, 255)),
        ("OTHER:", (150, 255, 150)),
        ("  Green Sphere - Goal!", (100, 255, 100)),
        ("  Purple Disc - Teleport pad", (200, 100, 255)),
        ("  Yellow Mark - Your glow stick", (255, 255, 100)),
    ]
    
    for text, color in items:
        if text:
            text_surf = text_font.render(text, True, color, (0, 0, 0))
            text_data = pygame.image.tostring(text_surf, "RGBA", True)
            glWindowPos2d(x_pos + 10, y_pos)
            glDrawPixels(text_surf.get_width(), text_surf.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, text_data)
        y_pos -= 25
    
    # Bottom message
    msg_surf = text_font.render("Press H to close help", True, (255, 255, 100), (0, 0, 0))
    msg_data = pygame.image.tostring(msg_surf, "RGBA", True)
    glWindowPos2d(400, 20)
    glDrawPixels(msg_surf.get_width(), msg_surf.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, msg_data)


def main():
    pygame.init()
    display = (1000, 800)
    screen = pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    pygame.display.set_caption("3D Maze Game - COSC 4370")
    
    
    # OpenGL settings
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glShadeModel(GL_SMOOTH)
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
    
    glEnable(GL_LIGHT0)
    glLightfv(GL_LIGHT0, GL_AMBIENT, [0.5, 0.5, 0.5, 1])
    glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 1.0, 1.0, 1])
    
    # Perspective
    glMatrixMode(GL_PROJECTION)
    gluPerspective(45, (display[0] / display[1]), 0.1, 50.0)
    glMatrixMode(GL_MODELVIEW)
    
    # Generate maze
    MAZE_SIZE = 10
    CELL_SIZE = 2.0
    WALL_HEIGHT = 2.0
    
    maze = Maze(MAZE_SIZE, MAZE_SIZE)
    maze.generate_prim()
    
    # Load textures
    wall_texture = load_texture('Homework 5/textures/rough_plaster_03_4k/textures/rough_plaster_03_diff_4k.jpg')
    floor_texture = load_texture('Homework 5/textures/brick_pavement_02_4k/textures/brick_pavement_02_diff_4k.jpg')
    
    print("Maze generated!")
    print("Controls:")
    print("  WASD - Move")
    print("  Mouse - Look around")
    print("  1 - Break wall (when holding wall breaker)")
    print("  3 - Drop glow stick marker (3 total)")
    print("  T - Teleport (when on teleport pad)")
    print("  ESC - Exit")
    print("  R - Reset position")
    print("  N - Generate new maze")
    print("")
    print("Power-ups:")
    print("  Orange cube = Wall breaker (break 1 wall)")
    print("  Cyan torus = Shield (blocks next trap)")
    print("Traps:")
    print("  Red spheres = Reset (sends you to start, one-time use)")
    print("  Dark gray spheres = Dark zone (limits vision for 15s)")
    print("  Pink spheres = Invert (inverts controls for 15s)")
    print("Other:")
    print("  Purple discs = Teleport pads (reusable)")
    print("  Yellow cylinders = Your glow stick markers")
    print("  Green sphere = Goal")
    
    # EXPLICIT position tracking - no more matrix extraction!
    player_x = CELL_SIZE / 2
    player_y = CELL_SIZE / 2
    player_z = 1.0  # Eye height
    
    # Camera angles
    yaw = 90.0  # Left-right rotation (starts facing +Y)
    pitch = 0.0  # Up-down rotation
    
    # Timer
    start_time = pygame.time.get_ticks()
    
    # Win state
    has_won = False
    win_time = 0
    
    # Glow sticks (markers)
    glow_sticks = []  # List of (x, y, z, yaw) - position + direction
    max_glow_sticks = 3
    
    # Wall breaker power-up
    has_wall_breaker = False
    wb_r, wb_c = get_safe_random_pos(maze)
    wall_breaker_pos = (wb_r, wb_c)
    print(f"Wall breaker placed at ({wb_c}, {wb_r})!")
    
    # Shield power-up
    has_shield = False
    sh_r, sh_c = get_safe_random_pos(maze, [(wb_r, wb_c)])
    shield_pos = (sh_r, sh_c)
    print(f"Shield placed at ({sh_c}, {sh_r})!")
    
    # Traps - place some reset traps randomly in the maze
    import random
    reset_traps = []
    dark_traps = []
    invert_traps = []
    num_reset_traps = 2
    num_dark_traps = 3
    num_invert_traps = 3
    
    for _ in range(num_reset_traps):
        trap_r = random.randint(1, maze.rows - 2)
        trap_c = random.randint(1, maze.cols - 2)
        if not (trap_r == 0 and trap_c == 0):
            reset_traps.append((trap_r, trap_c))
    
    for _ in range(num_dark_traps):
        trap_r = random.randint(1, maze.rows - 2)
        trap_c = random.randint(1, maze.cols - 2)
        if not (trap_r == 0 and trap_c == 0):
            dark_traps.append((trap_r, trap_c))
    
    for _ in range(num_invert_traps):
        trap_r = random.randint(1, maze.rows - 2)
        trap_c = random.randint(1, maze.cols - 2)
        if not (trap_r == 0 and trap_c == 0):
            invert_traps.append((trap_r, trap_c))
    
    # Trap effects state
    dark_zone_end_time = 0
    invert_controls_end_time = 0
    
    # Teleport pads - place some teleport pads
    teleport_pads = []
    num_teleports = 2
    for _ in range(num_teleports):
        tp_r = random.randint(1, maze.rows - 2)
        tp_c = random.randint(1, maze.cols - 2)
        if not (tp_r == 0 and tp_c == 0):  # Not at start
            teleport_pads.append((tp_r, tp_c))
    
    # Teleport state
    on_teleport_pad = False
    last_teleport_cell = None
    teleport_confirmation_pending = False
    
    # Help screen state
    show_help = False
    
    print(f"Placed {len(reset_traps)} reset traps, {len(dark_traps)} dark traps, {len(invert_traps)} invert traps!")
    print(f"Placed {len(teleport_pads)} teleport pads!")
    print("Press H at any time to toggle help screen!")
    
    # Initialize font for HUD
    pygame.font.init()
    font = pygame.font.SysFont('Arial', 24)
    
    # Mouse control
    displayCenter = [screen.get_size()[i] // 2 for i in range(2)]
    pygame.mouse.set_pos(displayCenter)
    
    run = True
    clock = pygame.time.Clock()
    
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    run = False
                if event.key == pygame.K_h:
                    show_help = not show_help
                    print(f"Help screen: {'ON' if show_help else 'OFF'}")
                if event.key == pygame.K_r:
                    player_x = CELL_SIZE / 2
                    player_y = CELL_SIZE / 2
                    player_z = 1.0
                    yaw = 90.0
                    pitch = 0.0
                    pygame.mouse.set_pos(displayCenter)
                    start_time = pygame.time.get_ticks()
                    has_won = False
                    win_time = 0
                    glow_sticks = []
                    has_wall_breaker = False
                    has_shield = False
                    wb_r, wb_c = get_safe_random_pos(maze)
                    wall_breaker_pos = (wb_r, wb_c)
                    sh_r, sh_c = get_safe_random_pos(maze, [(wb_r, wb_c)])
                    shield_pos = (sh_r, sh_c)
                    dark_zone_end_time = 0
                    invert_controls_end_time = 0
                    on_teleport_pad = False
                    teleport_confirmation_pending = False
                    last_teleport_cell = None
                    print("Position reset!")
                if event.key == pygame.K_n:
                    maze = Maze(MAZE_SIZE, MAZE_SIZE)
                    maze.generate_prim()
                    player_x = CELL_SIZE / 2
                    player_y = CELL_SIZE / 2
                    player_z = 1.0
                    yaw = 90.0
                    pitch = 0.0
                    pygame.mouse.set_pos(displayCenter)
                    start_time = pygame.time.get_ticks()
                    has_won = False
                    win_time = 0
                    glow_sticks = []
                    has_wall_breaker = False
                    has_shield = False
                    wb_r, wb_c = get_safe_random_pos(maze)
                    wall_breaker_pos = (wb_r, wb_c)
                    sh_r, sh_c = get_safe_random_pos(maze, [(wb_r, wb_c)])
                    shield_pos = (sh_r, sh_c)
                    # Generate new traps
                    reset_traps = []
                    dark_traps = []
                    invert_traps = []
                    for _ in range(num_reset_traps):
                        trap_r = random.randint(1, maze.rows - 2)
                        trap_c = random.randint(1, maze.cols - 2)
                        if not (trap_r == 0 and trap_c == 0):
                            reset_traps.append((trap_r, trap_c))
                    for _ in range(num_dark_traps):
                        trap_r = random.randint(1, maze.rows - 2)
                        trap_c = random.randint(1, maze.cols - 2)
                        if not (trap_r == 0 and trap_c == 0):
                            dark_traps.append((trap_r, trap_c))
                    for _ in range(num_invert_traps):
                        trap_r = random.randint(1, maze.rows - 2)
                        trap_c = random.randint(1, maze.cols - 2)
                        if not (trap_r == 0 and trap_c == 0):
                            invert_traps.append((trap_r, trap_c))
                    # Generate new teleport pads
                    teleport_pads = []
                    for _ in range(num_teleports):
                        tp_r = random.randint(1, maze.rows - 2)
                        tp_c = random.randint(1, maze.cols - 2)
                        if not (tp_r == 0 and tp_c == 0):
                            teleport_pads.append((tp_r, tp_c))
                    dark_zone_end_time = 0
                    invert_controls_end_time = 0
                    on_teleport_pad = False
                    teleport_confirmation_pending = False
                    last_teleport_cell = None
                    print("New maze generated!")
                if event.key == pygame.K_3:
                    # Place glow stick
                    if len(glow_sticks) < max_glow_sticks:
                        glow_sticks.append((player_x, player_y, player_z, yaw))
                        print(f"Glow stick placed! ({max_glow_sticks - len(glow_sticks)} remaining)")
                    else:
                        print("No glow sticks remaining!")
                if event.key == pygame.K_1:
                    # Use wall breaker
                    if has_wall_breaker:
                        # Determine which wall the player is looking at
                        cell_c = int(player_x / CELL_SIZE)
                        cell_r = int(player_y / CELL_SIZE)
                        
                        # Calculate look direction in 2D (ignore pitch)
                        yaw_rad = math.radians(yaw)
                        look_x = math.cos(yaw_rad)
                        look_y = math.sin(yaw_rad)
                        
                        # Determine which direction has strongest component
                        abs_x = abs(look_x)
                        abs_y = abs(look_y)
                        
                        wall_dir = None
                        target_cell_r = cell_r
                        target_cell_c = cell_c
                        
                        if abs_x > abs_y:
                            if look_x > 0:
                                wall_dir = 1  # East
                                target_cell_c += 1
                            else:
                                wall_dir = 3  # West
                                target_cell_c -= 1
                        else:
                            if look_y > 0:
                                wall_dir = 0  # North (looking in +Y direction, but wall index 0 is north which is -Y 
                                target_cell_r -= 1
                            else:
                                wall_dir = 2  # South
                                target_cell_r += 1
                        
                        # row 0 is at y=0 (north), row increases going south (+Y)
                        # So North wall is at the -Y side (towards row-1)
                        # Recalculate properly:
                        if abs_y > abs_x:
                            if look_y > 0:
                                wall_dir = 2  # South (going to higher row)
                            else:
                                wall_dir = 0  # North (going to lower row)
                        else:
                            if look_x > 0:
                                wall_dir = 1  # East
                            else:
                                wall_dir = 3  # West
                        
                        # check if wall exists
                        idx = maze.index(cell_r, cell_c)
                        if maze.grid[idx].wall[wall_dir]:
                            # Check if its an outer wall
                            is_outer = False
                            if cell_r == 0 and wall_dir == 0:  # North wall of top row
                                is_outer = True
                            elif cell_r == maze.rows - 1 and wall_dir == 2:  # South wall of bottom row
                                is_outer = True
                            elif cell_c == 0 and wall_dir == 3:  # West wall of left column
                                is_outer = True
                            elif cell_c == maze.cols - 1 and wall_dir == 1:  # East wall of right column
                                is_outer = True
                            
                            if not is_outer:
                                # break the wall
                                maze.grid[idx].wall[wall_dir] = False
                                # also break the opposite wall of the adjacent cell
                                if wall_dir == 0 and cell_r > 0:
                                    adj_idx = maze.index(cell_r - 1, cell_c)
                                    maze.grid[adj_idx].wall[2] = False
                                elif wall_dir == 1 and cell_c < maze.cols - 1:
                                    adj_idx = maze.index(cell_r, cell_c + 1)
                                    maze.grid[adj_idx].wall[3] = False
                                elif wall_dir == 2 and cell_r < maze.rows - 1:
                                    adj_idx = maze.index(cell_r + 1, cell_c)
                                    maze.grid[adj_idx].wall[0] = False
                                elif wall_dir == 3 and cell_c > 0:
                                    adj_idx = maze.index(cell_r, cell_c - 1)
                                    maze.grid[adj_idx].wall[1] = False
                                
                                has_wall_breaker = False
                                print("WALL BROKEN!")
                            else:
                                print("Cannot break outer maze walls!")
                        else:
                            print("No wall in that direction!")
                    else:
                        print("Don't have wall breaker!")
                if event.key == pygame.K_t:
                    # Confirm teleport
                    if teleport_confirmation_pending:
                        # Teleport to random valid location
                        valid_cells = []
                        for r in range(maze.rows):
                            for c in range(maze.cols):
                                # Don't teleport to start or goal
                                if not (r == 0 and c == 0) and not (r == maze.rows-1 and c == maze.cols-1):
                                    valid_cells.append((r, c))
                        
                        if valid_cells:
                            tp_r, tp_c = random.choice(valid_cells)
                            player_x = tp_c * CELL_SIZE + CELL_SIZE / 2
                            player_y = tp_r * CELL_SIZE + CELL_SIZE / 2
                            player_z = 1.0
                            print(f"TELEPORTED to ({tp_c}, {tp_r})!")
                        
                        teleport_confirmation_pending = False
        
        # Mouse movement
        mouse_pos = pygame.mouse.get_pos()
        mouse_dx = mouse_pos[0] - displayCenter[0]
        mouse_dy = mouse_pos[1] - displayCenter[1]
        pygame.mouse.set_pos(displayCenter)
        
        # Check if controls are inverted
        current_time = pygame.time.get_ticks()
        controls_inverted = current_time < invert_controls_end_time
        
        # Update camera angles (invert if needed)
        if controls_inverted:
            yaw += mouse_dx * 0.1  # Inverted
            pitch += mouse_dy * 0.1  # Inverted
        else:
            yaw -= mouse_dx * 0.1
            pitch -= mouse_dy * 0.1
        pitch = max(-80, min(80, pitch))
        
        # Get keyboard input
        keys = pygame.key.get_pressed()
        
        # Movement speed
        move_speed = 0.05
        
        # Calculate forward and right vectors based on yaw
        yaw_rad = math.radians(yaw)
        forward_x = math.cos(yaw_rad)
        forward_y = math.sin(yaw_rad)
        right_x = math.cos(yaw_rad - math.pi/2)
        right_y = math.sin(yaw_rad - math.pi/2)
        
        # Calculate new position based on input (invert if needed)
        new_x = player_x
        new_y = player_y
        new_z = player_z
        
        if controls_inverted:
            # Inverted controls
            if keys[K_w]:
                new_x -= forward_x * move_speed
                new_y -= forward_y * move_speed
            if keys[K_s]:
                new_x += forward_x * move_speed
                new_y += forward_y * move_speed
            if keys[K_a]:
                new_x += right_x * move_speed
                new_y += right_y * move_speed
            if keys[K_d]:
                new_x -= right_x * move_speed
                new_y -= right_y * move_speed
        else:
            # Normal controls
            if keys[K_w]:
                new_x += forward_x * move_speed
                new_y += forward_y * move_speed
            if keys[K_s]:
                new_x -= forward_x * move_speed
                new_y -= forward_y * move_speed
            if keys[K_a]:
                new_x -= right_x * move_speed
                new_y -= right_y * move_speed
            if keys[K_d]:
                new_x += right_x * move_speed
                new_y += right_y * move_speed
            # if keys[K_SPACE]:
            #     new_z += move_speed
            # if keys[K_LSHIFT]:
            #     new_z -= move_speed
        
        # Check collision and update position
        if not check_wall_collision(maze, new_x, new_y, CELL_SIZE):
            player_x = new_x
            player_y = new_y
        # player_z = new_z 
        
        # Check win condition
        if not has_won:
            cell_c = int(player_x / CELL_SIZE)
            cell_r = int(player_y / CELL_SIZE)
            goal_c = maze.cols - 1
            goal_r = maze.rows - 1
            
            if cell_c == goal_c and cell_r == goal_r:
                has_won = True
                win_time = pygame.time.get_ticks() - start_time
                print(f"YOU WIN! Time: {win_time/1000.0:.2f} seconds")
            
            # Check for trap collision (all types)
            # Reset traps
            for trap_r, trap_c in reset_traps[:]:
                if cell_c == trap_c and cell_r == trap_r:
                    if has_shield:
                        has_shield = False
                        reset_traps.remove((trap_r, trap_c))
                        print("SHIELD blocked reset trap!")
                    else:
                        print("RESET TRAP! Back to start (timer keeps running, glow sticks stay)")
                        player_x = CELL_SIZE / 2
                        player_y = CELL_SIZE / 2
                        player_z = 1.0
                        reset_traps.remove((trap_r, trap_c))
                    break
            
            # Dark zone traps
            for trap_r, trap_c in dark_traps[:]:
                if cell_c == trap_c and cell_r == trap_r:
                    if has_shield:
                        has_shield = False
                        dark_traps.remove((trap_r, trap_c))
                        print("SHIELD blocked dark zone trap!")
                    else:
                        dark_zone_end_time = pygame.time.get_ticks() + 15000  # 15 seconds
                        dark_traps.remove((trap_r, trap_c))
                        print("DARK ZONE! Limited vision for 15 seconds!")
                    break
            
            # Invert controls traps
            for trap_r, trap_c in invert_traps[:]:
                if cell_c == trap_c and cell_r == trap_r:
                    if has_shield:
                        has_shield = False
                        invert_traps.remove((trap_r, trap_c))
                        print("SHIELD blocked invert trap!")
                    else:
                        invert_controls_end_time = pygame.time.get_ticks() + 15000  # 15 seconds
                        invert_traps.remove((trap_r, trap_c))
                        print("INVERTED CONTROLS! Controls inverted for 15 seconds!")
                    break
            
            # Check for teleport pad
            current_cell = (cell_r, cell_c)
            if current_cell in [(tp_r, tp_c) for tp_r, tp_c in teleport_pads]:
                if not on_teleport_pad or last_teleport_cell != current_cell:
                    # First time stepping on this pad (or re-entering it)
                    on_teleport_pad = True
                    last_teleport_cell = current_cell
                    teleport_confirmation_pending = True
                    print("TELEPORT PAD! Press 'T' to teleport to random location")
            else:
                # Not on any teleport pad
                if on_teleport_pad:
                    on_teleport_pad = False
                    teleport_confirmation_pending = False
            
            # Check for wall breaker pickup
            if wall_breaker_pos and not has_wall_breaker:
                wb_r, wb_c = wall_breaker_pos
                if cell_r == wb_r and cell_c == wb_c:
                    has_wall_breaker = True
                    wall_breaker_pos = None  # Remove from world
                    print("WALL BREAKER picked up! Press '1' to break a wall")
            
            # Check for shield pickup
            if shield_pos and not has_shield:
                sh_r, sh_c = shield_pos
                if cell_r == sh_r and cell_c == sh_c:
                    has_shield = True
                    shield_pos = None  # Remove from world
                    print("SHIELD picked up! Blocks next trap!")
        
        # Set up camera view
        glLoadIdentity()
        
        # Look direction
        look_x = player_x + math.cos(math.radians(yaw)) * math.cos(math.radians(pitch))
        look_y = player_y + math.sin(math.radians(yaw)) * math.cos(math.radians(pitch))
        look_z = player_z + math.sin(math.radians(pitch))
        
        gluLookAt(
            player_x, player_y, player_z,  # Camera position
            look_x, look_y, look_z,        # Look at point
            0, 0, 1                         # Up vector
        )
        
        # Draw everything
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        maze_center_x = (maze.cols * CELL_SIZE) / 2
        maze_center_y = (maze.rows * CELL_SIZE) / 2
        light_height = WALL_HEIGHT * 3.0
        glLightfv(GL_LIGHT0, GL_POSITION, [maze_center_x, maze_center_y, light_height, 1.0])
        
        # Set up glow stick lights (point lights)
        # Disable extra lights first
        for i in range(1, 8):
            glDisable(GL_LIGHT0 + i)
        
        # Add green light for goal sphere (use LIGHT1)
        goal_r = maze.rows - 1
        goal_c = maze.cols - 1
        goal_x = goal_c * CELL_SIZE + CELL_SIZE / 2
        goal_y = goal_r * CELL_SIZE + CELL_SIZE / 2
        goal_z = 1.0
    
        glEnable(GL_LIGHT1)
        glLightfv(GL_LIGHT1, GL_POSITION, [goal_x, goal_y, goal_z, 1.0])
        glLightfv(GL_LIGHT1, GL_AMBIENT, [0.0, 0.3, 0.0, 1.0])
        glLightfv(GL_LIGHT1, GL_DIFFUSE, [0.0, 1.5, 0.0, 1.0])  # Bright green
        glLightfv(GL_LIGHT1, GL_SPECULAR, [0.0, 0.8, 0.0, 1.0])
        glLightf(GL_LIGHT1, GL_CONSTANT_ATTENUATION, 1.0)
        glLightf(GL_LIGHT1, GL_LINEAR_ATTENUATION, 0.2)
        glLightf(GL_LIGHT1, GL_QUADRATIC_ATTENUATION, 0.08)
        
        # Enable one light per glow stick (up to 6, since LIGHT0 is global and light 1 is goal)
        for idx, (gx, gy, gz, gyaw) in enumerate(glow_sticks[:6]):  # Max 6 glow sticks can have lights
            light_id = GL_LIGHT0 + idx + 2  # LIGHT2, LIGHT3, etc.
            glEnable(light_id)
            
            # Position the light at the glow stick location
            glLightfv(light_id, GL_POSITION, [gx, gy, 0.05, 1.0])  # w=1.0 means point light
            
            # Yellow/warm light color
            glLightfv(light_id, GL_AMBIENT, [0.3, 0.3, 0.1, 1.0])
            glLightfv(light_id, GL_DIFFUSE, [1.0, 1.0, 0.3, 1.0])
            glLightfv(light_id, GL_SPECULAR, [0.5, 0.5, 0.2, 1.0])
            
            # Attenuation (makes light fade with distance)
            glLightf(light_id, GL_CONSTANT_ATTENUATION, 1.0)
            glLightf(light_id, GL_LINEAR_ATTENUATION, 0.3)
            glLightf(light_id, GL_QUADRATIC_ATTENUATION, 0.1)
        
        # Apply dark zone fog effect if active
        if current_time < dark_zone_end_time:
            glEnable(GL_FOG)
            glFogi(GL_FOG_MODE, GL_EXP2)
            glFogfv(GL_FOG_COLOR, [0.0, 0.0, 0.0, 1.0])
            glFogf(GL_FOG_DENSITY, 0.3)  # Thick fog
        else:
            glDisable(GL_FOG)
        
        glPushMatrix()
        draw_floor_ceiling(maze, CELL_SIZE, WALL_HEIGHT, floor_texture)
        draw_maze_walls(maze, CELL_SIZE, WALL_HEIGHT, wall_texture)
        draw_goal_marker(maze, CELL_SIZE)
        draw_traps(reset_traps, CELL_SIZE)
        draw_dark_traps(dark_traps, CELL_SIZE)
        draw_invert_traps(invert_traps, CELL_SIZE)
        draw_teleport_pads(teleport_pads, CELL_SIZE)
        draw_wall_breaker(wall_breaker_pos, CELL_SIZE)
        draw_shield(shield_pos, CELL_SIZE)
        draw_glow_sticks(glow_sticks)
        glPopMatrix()
        
        # Draw HUD
        elapsed = pygame.time.get_ticks() - start_time
        glow_remaining = max_glow_sticks - len(glow_sticks)
        dark_active = current_time < dark_zone_end_time
        invert_active = current_time < invert_controls_end_time
        draw_hud(font, elapsed, player_x, player_y, CELL_SIZE, has_won, win_time, glow_remaining, teleport_confirmation_pending, has_wall_breaker, has_shield, dark_active, invert_active)
        
        # Draw help overlay if toggled on
        if show_help:
            draw_help_overlay(font)
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()


if __name__ == "__main__":
    main()