from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import random
import time

# Window configuration
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 800
ASPECT_RATIO = WINDOW_WIDTH / float(WINDOW_HEIGHT)
FIELD_OF_VIEW = 70.0

# Aircraft state
aircraft_position = [0.0, 0.0, 120.0]
rotation_yaw = 0.0
rotation_pitch = 0.0
rotation_roll = 0.0
velocity = 1.2
propeller_rotation = 0.0
stored_velocity = 1.2

# Barrel roll system
barrel_roll_active = False
barrel_roll_angle = 0.0
BARREL_ROLL_SPEED = 5.0      # degrees per frame
BARREL_ROLL_INVINCIBLE_TIME = 2.0  # seconds
barrel_roll_end_time = 0.0


# Projectile system
projectiles = []
PROJECTILE_VELOCITY = 20.0
PROJECTILE_DURATION = 2500

# Game status
status = {
    'mode': 'Obstacle Run',
    'hp': 100,
    'points': 0,
    'init_time': None,
    'enhanced_power': False,
    'invincibility': False,
    'ended': False,
    'stage': 1,
    'time_limit': 60,
    'bonus_mode': False,
    'bonus_end': 0,
}

# Camera configuration
camera_distance = 120.0
camera_elevation = 35.0
camera_lateral = 0.0
camera_shift_x = 0.0
camera_shift_y = 0.0
camera_shift_z = 0.0

# Mini-map configuration
MINIMAP_SIZE = 200
MINIMAP_MARGIN = 10
MINIMAP_RANGE = 500.0
show_minimap = True

# Environment objects
CLOUD_COUNT = 60
CLOUD_FORWARD_DIST = 4000.0
CLOUD_LATERAL_DIST = 2000.0
CLOUD_HEIGHT_MIN = -200.0
CLOUD_HEIGHT_MAX = 350.0
cloud_objects = []

OBSTACLE_COUNT = 50
COLLECTIBLE_COUNT = 100
SPAWN_FORWARD = 2500.0
SPAWN_LATERAL = 1500.0
SPAWN_HEIGHT_MIN = -200.0
SPAWN_HEIGHT_MAX = 200.0
obstacle_objects = []
collectible_objects = []

RARE_COLLECTIBLE_CHANCE = 0.1
rare_collectible_present = False
normal_collectibles_spawned = 0
BASE_VELOCITY = 5
VELOCITY_MAX = 50.0
VELOCITY_MIN = 0.5
VELOCITY_DELTA = 0.01

# Weather system
precipitation = []
WEATHER_ACTIVE = False
WEATHER_START = time.time() + 10
WEATHER_CYCLE = 30
WEATHER_LENGTH = 10
PRECIPITATION_COUNT = 1000
PRECIPITATION_AREA = 2000
PRECIPITATION_ALTITUDE = 4000
PRECIPITATION_FALL_RATE = 50
PRECIPITATION_TRAIL = 30

# =========================
# FOG SYSTEM
# =========================
FOG_ACTIVE = False
FOG_START = 300.0     # distance where fog begins
FOG_END = 1200.0      # distance where fog fully blocks view
FOG_COLOR = [0.7, 0.7, 0.75, 1.0]

transitioning_weather = False
transition_begin = 0.0
transition_time = 1.0

clear_sky = (0.5, 0.7, 1.0)
storm_sky = (0.4, 0.45, 0.5)
active_sky = list(clear_sky)

rare_item_position = [random.uniform(-15, 15), random.uniform(-15, 15), random.uniform(-15, -5)]
rare_item_rotation = 0

quadric_object = None

input_state = {
    GLUT_LEFT_BUTTON: False,
    GLUT_RIGHT_BUTTON: False
}

first_person_view = False

def restart_simulation():
    global aircraft_position, rotation_yaw, rotation_pitch, rotation_roll, velocity
    global propeller_rotation, stored_velocity, projectiles, status
    global camera_shift_x, camera_shift_y, camera_shift_z
    global cloud_objects, obstacle_objects, collectible_objects
    global rare_collectible_present, normal_collectibles_spawned
    global precipitation, WEATHER_ACTIVE, WEATHER_START
    global transitioning_weather, active_sky, first_person_view
    
    aircraft_position = [0.0, 0.0, 120.0]
    rotation_yaw = 0.0
    rotation_pitch = 0.0
    rotation_roll = 0.0
    velocity = 1.2
    propeller_rotation = 0.0
    stored_velocity = 1.2
    
    projectiles = []
    
    status['mode'] = 'Obstacle Run'
    status['hp'] = 100
    status['points'] = 0
    status['init_time'] = time.time()
    status['enhanced_power'] = False
    status['invincibility'] = False
    status['ended'] = False
    status['stage'] = 1
    status['time_limit'] = 60
    status['bonus_mode'] = False
    status['bonus_end'] = 0
    
    camera_shift_x = 0.0
    camera_shift_y = 0.0
    camera_shift_z = 0.0
    first_person_view = False
    show_minimap = True
    
    cloud_objects = []
    obstacle_objects = []
    collectible_objects = []
    rare_collectible_present = False
    normal_collectibles_spawned = 0
    
    precipitation = []
    WEATHER_ACTIVE = False
    WEATHER_START = time.time() + 10
    transitioning_weather = False
    active_sky = list(clear_sky)

    populate_clouds()
    populate_obstacles_collectibles()
    print("Simulation restarted.")
    glutPostRedisplay()

def to_radians(degrees):
    return degrees * math.pi / 180.0

def get_forward_direction():
    y_rad = to_radians(rotation_yaw)
    p_rad = to_radians(rotation_pitch)
    forward_x = math.sin(y_rad) * math.cos(p_rad)
    forward_y = math.cos(y_rad) * math.cos(p_rad)
    forward_z = math.sin(p_rad)
    return (forward_x, forward_y, forward_z)

def get_up_direction(forward, right):
    up_x = right[1] * forward[2] - right[2] * forward[1]
    up_y = right[2] * forward[0] - right[0] * forward[2]
    up_z = right[0] * forward[1] - right[1] * forward[0]
    return (up_x, up_y, up_z)

def get_right_direction(forward):
    world_up = (0.0, 0.0, 1.0)
    right_x = forward[1] * world_up[2] - forward[2] * world_up[1]
    right_y = forward[2] * world_up[0] - forward[0] * world_up[2]
    right_z = forward[0] * world_up[1] - forward[1] * world_up[0]
    magnitude = math.sqrt(right_x**2 + right_y**2 + right_z**2) or 1.0
    return (right_x / magnitude, right_y / magnitude, right_z / magnitude)

def vector_add(vec_a, vec_b, scale=1.0):
    return [vec_a[0] + scale * vec_b[0], 
            vec_a[1] + scale * vec_b[1], 
            vec_a[2] + scale * vec_b[2]]

def render_sky_background():
    glDisable(GL_DEPTH_TEST)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glBegin(GL_QUADS)
    glColor3f(active_sky[0], active_sky[1], active_sky[2])
    glVertex2f(0, 0)
    glVertex2f(WINDOW_WIDTH, 0)
    glColor3f(active_sky[0] + 0.3, active_sky[1] + 0.2, active_sky[2] + 0.1)
    glVertex2f(WINDOW_WIDTH, WINDOW_HEIGHT)
    glVertex2f(0, WINDOW_HEIGHT)
    glEnd()
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glEnable(GL_DEPTH_TEST)

def render_cloud_shape():
    glColor3f(0.8039, 0.9411, 1.0)
    glPushMatrix()
    glScalef(1.0, 0.8, 0.8)
    glutSolidSphere(18, 20, 16)
    glTranslatef(12, 5, 2)
    glutSolidSphere(14, 18, 14)
    glTranslatef(-20, -10, 3)
    glutSolidSphere(15, 18, 14)
    glTranslatef(10, 10, 10)
    glutSolidSphere(12, 18, 14)
    glTranslatef(8, -4, -12)
    glutSolidSphere(10, 16, 12)
    glPopMatrix()

def render_all_clouds():
    for cloud in cloud_objects:
        glPushMatrix()
        glTranslatef(cloud['position'][0], cloud['position'][1], cloud['position'][2])
        glScalef(cloud['size'], cloud['size'], cloud['size'])
        render_cloud_shape()
        glPopMatrix()

def render_obstacle_shape():
    glColor3f(1.0, 0.0, 0.0)
    glPushMatrix()
    glScalef(1.0, 1.0, 3.0)
    glutSolidCube(20)
    glPopMatrix()

def render_target_ring():
    glColor3f(0.8, 0.8, 0.1)
    glutSolidTorus(5, 12, 12, 24)

def render_collectible_item(rare=False):
    if rare:
        global rare_item_rotation
        scale_factor = 1.2 + 0.4 * math.sin(rare_item_rotation * math.pi / 180)
        glPushMatrix()
        glRotatef(90, 1, 0, 0)
        glColor3f(1, 0.5, 0)
        glutWireTorus(0.2, scale_factor + 0.3, 16, 32)
        glPopMatrix()
        rare_item_rotation = (rare_item_rotation + 2) % 360
    else:
        glColor3f(0.85, 0.85, 0.1)
        glPushMatrix()
        glutSolidSphere(8, 16, 16)
        glPopMatrix()

def render_projectile_shape():
    glPushAttrib(GL_LIGHTING_BIT)
    glPushMatrix()
    glRotatef(90, 1, 0, 0)
    glShadeModel(GL_SMOOTH)
    segments = 24
    base_radius = 8.0
    cone_height = 20.0
    glBegin(GL_TRIANGLE_FAN)
    glColor3f(0.8, 0.7, 0.0)
    glVertex3f(0.0, 0.0, cone_height)
    for idx in range(segments + 1):
        theta = 2 * math.pi * idx / segments
        x_pos = base_radius * math.cos(theta)
        y_pos = base_radius * math.sin(theta)
        glColor3f(1.0, 0.5, 0.0)
        glVertex3f(x_pos, y_pos, 0.0)
    glEnd()
    glBegin(GL_TRIANGLE_FAN)
    glColor3f(1.0, 0.5, 0.0)
    glVertex3f(0.0, 0.0, 0.0)
    for idx in range(segments + 1):
        theta = 2 * math.pi * idx / segments
        x_pos = base_radius * math.cos(theta)
        y_pos = base_radius * math.sin(theta)
        glVertex3f(x_pos, y_pos, 0.0)
    glEnd()
    glPopMatrix()
    glPopAttrib()

def render_pilot_character():
    glPushMatrix()
    glColor3f(0.0, 0.0, 0.0)
    glPushMatrix()
    glTranslatef(0, 0, 5)
    glScalef(1.2, 1.2, 1.4)
    glutSolidSphere(4, 16, 16)
    glPopMatrix()
    glColor3f(0.4, 0.4, 0.4)
    glPushMatrix()
    glTranslatef(0, 0, 6)
    glScalef(1.0, 1.0, 1.0)
    glutSolidSphere(3, 16, 16)
    glPopMatrix()
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glDepthMask(GL_FALSE)
    glColor4f(0.5, 0.8, 1.0, 0.5)
    glPushMatrix()
    glTranslatef(0, 0, 5.5)
    glRotatef(90, 1, 0, 0)
    gluPartialDisk(quadric_object, 0, 3.5, 16, 1, 0, 180)
    glPopMatrix()
    glDepthMask(GL_TRUE)
    glDisable(GL_BLEND)
    glColor3f(0.1, 0.1, 0.8)
    glPushMatrix()
    glTranslatef(0, 0, -3)
    glRotatef(-90, 1, 0, 0)
    gluCylinder(quadric_object, 5, 3, 8, 16, 1)
    glPopMatrix()
    glColor3f(0.1, 0.1, 0.8)
    for side_offset in [-5.5, 5.5]:
        glPushMatrix()
        glTranslatef(side_offset, 0, -3)
        glRotatef(90, 0, 1, 0)
        glRotatef(15, 1, 0, 0)
        gluCylinder(quadric_object, 1.5, 1.5, 4, 12, 1)
        glTranslatef(0, 0, 4)
        gluCylinder(quadric_object, 1.3, 1.3, 3, 12, 1)
        glTranslatef(0, 0, 3)
        glColor3f(1.0, 0.8, 0.6)
        glutSolidSphere(1.5, 8, 8)
        glPopMatrix()
    glPopMatrix()

def render_aircraft():
    glPushMatrix()
    glTranslatef(aircraft_position[0], aircraft_position[1], aircraft_position[2])
    glRotatef(rotation_yaw, 0, 0, 1)
    glRotatef(rotation_pitch, 1, 0, 0)
    glRotatef(rotation_roll, 0, 1, 0)
    
    BODY_COLOR = (0.2, 0.2, 0.2)
    STRIPE_COLOR = (1.0, 1.0, 1.0)
    WING_COLOR = (0.9, 0.9, 0.9)
    TAIL_COLOR = (0.2, 0.2, 0.2)
    CANOPY_COLOR = (0.8, 0.8, 0.8, 0.5)
    WHEEL_COLOR = (0.1, 0.1, 0.1)
    STRUT_COLOR = (0.5, 0.5, 0.5)
    
    glPushMatrix()
    glRotatef(-90, 1, 0, 0)
    glColor3f(*BODY_COLOR)
    fuselage_length = 80.0
    fuselage_radius = 12.0
    gluCylinder(quadric_object, fuselage_radius, fuselage_radius, fuselage_length, 24, 2)
    glColor3f(*STRIPE_COLOR)
    glBegin(GL_QUADS)
    glVertex3f(-fuselage_radius, 0, 10)
    glVertex3f(fuselage_radius, 0, 10)
    glVertex3f(fuselage_radius, 0, 6)
    glVertex3f(-fuselage_radius, 0, 6)
    glEnd()
    glPushMatrix()
    glTranslatef(0, 0, fuselage_length)
    gluDisk(quadric_object, 0, fuselage_radius, 24, 1)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(0, 0, -5.0)
    gluCylinder(quadric_object, fuselage_radius, fuselage_radius * 0.6, 5.0, 24, 2)
    glPopMatrix()
    glPopMatrix()
    
    glPushMatrix()
    glTranslatef(0, 25, 0)
    glRotatef(90, 0, 1, 0)
    glBegin(GL_QUADS)
    glColor3f(*WING_COLOR)
    glVertex3f(-25, 0, -2)
    glVertex3f(-5, 0, -2)
    glVertex3f(-5, -50, 2)
    glVertex3f(-25, -50, 2)
    glVertex3f(25, 0, -2)
    glVertex3f(5, 0, -2)
    glVertex3f(5, -50, 2)
    glVertex3f(25, -50, 2)
    glEnd()
    glPopMatrix()
    
    glPushMatrix()
    glTranslatef(0, -50, 0)
    glBegin(GL_QUADS)
    glColor3f(*TAIL_COLOR)
    glVertex3f(-2, 0, 0)
    glVertex3f(2, 0, 0)
    glVertex3f(2, 0, 20)
    glVertex3f(-2, 0, 20)
    glEnd()
    glPopMatrix()
    
    glPushMatrix()
    glTranslatef(0, -45, 10)
    glBegin(GL_QUADS)
    glColor3f(*WING_COLOR)
    glVertex3f(-15, 0, 1)
    glVertex3f(-15, 0, -1)
    glVertex3f(-5, 0, -1)
    glVertex3f(-5, 0, 1)
    glVertex3f(15, 0, 1)
    glVertex3f(15, 0, -1)
    glVertex3f(5, 0, -1)
    glVertex3f(5, 0, 1)
    glEnd()
    glPopMatrix()
    
    glPushMatrix()
    glTranslatef(0, 70, -15)
    glColor3f(*STRUT_COLOR)
    glLineWidth(5.0)
    glBegin(GL_LINES)
    glVertex3f(0, 0, 0)
    glVertex3f(0, 0, -15)
    glEnd()
    glColor3f(*WHEEL_COLOR)
    glTranslatef(0, 0, -15)
    glutSolidTorus(2.0, 5.0, 10, 12)
    glPopMatrix()
    
    for wheel_side in [-1, 1]:
        glPushMatrix()
        glTranslatef(wheel_side * 20, 15, -10)
        glColor3f(*STRUT_COLOR)
        glLineWidth(5.0)
        glBegin(GL_LINES)
        glVertex3f(0, 0, 0)
        glVertex3f(0, 0, -10)
        glEnd()
        glColor3f(*WHEEL_COLOR)
        glTranslatef(0, 0, -10)
        glutSolidTorus(2.0, 5.0, 10, 12)
        glPopMatrix()
    
    glPushMatrix()
    glTranslatef(0, 30, 10)
    glScalef(0.8, 0.8, 0.8)
    render_pilot_character()
    glPopMatrix()
    
    glPushMatrix()
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glDepthMask(GL_FALSE)
    glTranslatef(0, 30, 10)
    glColor4f(*CANOPY_COLOR)
    glutSolidSphere(18, 20, 16)
    glDepthMask(GL_TRUE)
    glDisable(GL_BLEND)
    glPopMatrix()
    glPopMatrix()

def render_minimap():
    if not show_minimap:
        return
    
    # Save current viewport and projection
    glPushAttrib(GL_VIEWPORT_BIT)
    
    # Set minimap viewport (top-right corner)
    minimap_x = WINDOW_WIDTH - MINIMAP_SIZE - MINIMAP_MARGIN
    minimap_y = WINDOW_HEIGHT - MINIMAP_SIZE - MINIMAP_MARGIN - 100
    glViewport(minimap_x, minimap_y, MINIMAP_SIZE, MINIMAP_SIZE)
    
    # Switch to orthographic projection for 2D top-down view
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(-MINIMAP_RANGE, MINIMAP_RANGE, -MINIMAP_RANGE, MINIMAP_RANGE)
    
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    # Disable depth test for minimap
    glDisable(GL_DEPTH_TEST)
    
    # Draw minimap background
    glColor4f(0.0, 0.0, 0.0, 0.7)
    glBegin(GL_QUADS)
    glVertex2f(-MINIMAP_RANGE, -MINIMAP_RANGE)
    glVertex2f(MINIMAP_RANGE, -MINIMAP_RANGE)
    glVertex2f(MINIMAP_RANGE, MINIMAP_RANGE)
    glVertex2f(-MINIMAP_RANGE, MINIMAP_RANGE)
    glEnd()
    
    # Draw border
    glColor3f(1.0, 1.0, 1.0)
    glLineWidth(2.0)
    glBegin(GL_LINE_LOOP)
    glVertex2f(-MINIMAP_RANGE, -MINIMAP_RANGE)
    glVertex2f(MINIMAP_RANGE, -MINIMAP_RANGE)
    glVertex2f(MINIMAP_RANGE, MINIMAP_RANGE)
    glVertex2f(-MINIMAP_RANGE, MINIMAP_RANGE)
    glEnd()
    
    # Calculate relative positions to aircraft
    plane_x = aircraft_position[0]
    plane_y = aircraft_position[1]
    
    # Draw obstacles (red squares)
    glColor3f(1.0, 0.0, 0.0)
    for obs in obstacle_objects:
        rel_x = obs['position'][0] - plane_x
        rel_y = obs['position'][1] - plane_y
        
        # Only draw if within minimap range
        if abs(rel_x) < MINIMAP_RANGE and abs(rel_y) < MINIMAP_RANGE:
            size = 15.0
            glBegin(GL_QUADS)
            glVertex2f(rel_x - size, rel_y - size)
            glVertex2f(rel_x + size, rel_y - size)
            glVertex2f(rel_x + size, rel_y + size)
            glVertex2f(rel_x - size, rel_y + size)
            glEnd()
    
    # Draw collectibles (yellow circles)
    glColor3f(1.0, 1.0, 0.0)
    for col in collectible_objects:
        rel_x = col['position'][0] - plane_x
        rel_y = col['position'][1] - plane_y
        
        # Only draw if within minimap range
        if abs(rel_x) < MINIMAP_RANGE and abs(rel_y) < MINIMAP_RANGE:
            if col['category'] == 'special':
                # Draw special collectibles larger and orange
                glColor3f(1.0, 0.5, 0.0)
                size = 20.0
            else:
                glColor3f(1.0, 1.0, 0.0)
                size = 10.0
            
            # Draw circle
            glBegin(GL_TRIANGLE_FAN)
            glVertex2f(rel_x, rel_y)
            for i in range(13):
                angle = 2.0 * math.pi * i / 12
                x = rel_x + size * math.cos(angle)
                y = rel_y + size * math.sin(angle)
                glVertex2f(x, y)
            glEnd()
    
    # Draw aircraft (green triangle pointing forward)
    glColor3f(0.0, 1.0, 0.0)
    glPushMatrix()
    # Rotate to show aircraft orientation
    glRotatef(-rotation_yaw, 0, 0, 1)
    glBegin(GL_TRIANGLES)
    glVertex2f(0, 20)      # Nose
    glVertex2f(-15, -15)   # Left wing
    glVertex2f(15, -15)    # Right wing
    glEnd()
    # Draw aircraft center dot
    glColor3f(1.0, 1.0, 1.0)
    glBegin(GL_TRIANGLE_FAN)
    glVertex2f(0, 0)
    for i in range(13):
        angle = 2.0 * math.pi * i / 12
        x = 5 * math.cos(angle)
        y = 5 * math.sin(angle)
        glVertex2f(x, y)
    glEnd()
    glPopMatrix()
    
    # Draw range circles
    glColor4f(0.3, 0.3, 0.3, 0.5)
    glLineWidth(1.0)
    for radius in [MINIMAP_RANGE * 0.33, MINIMAP_RANGE * 0.66]:
        glBegin(GL_LINE_LOOP)
        for i in range(36):
            angle = 2.0 * math.pi * i / 36
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            glVertex2f(x, y)
        glEnd()
    
    # Restore matrices and settings
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    
    glEnable(GL_DEPTH_TEST)
    glPopAttrib()
    
    # Restore full viewport
    glViewport(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)

def render_text_overlay(x_pos, y_pos, message, font_type=GLUT_BITMAP_HELVETICA_18, text_color=(0, 0, 0)):
    glDisable(GL_DEPTH_TEST)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glColor3f(*text_color)
    glRasterPos2f(x_pos, y_pos)
    for character in message:
        glutBitmapCharacter(font_type, ord(character))
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glEnable(GL_DEPTH_TEST)

def configure_camera():
    global camera_shift_x, camera_shift_y, camera_shift_z, first_person_view
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(FIELD_OF_VIEW, ASPECT_RATIO, 0.1, 6000.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    forward = get_forward_direction()
    right = get_right_direction(forward)
    up = get_up_direction(forward, right)
    
    if first_person_view:
        eye_position = vector_add(aircraft_position, forward, 30.0)
        target_position = vector_add(eye_position, forward, 100.0)
        gluLookAt(eye_position[0], eye_position[1], eye_position[2],
                  target_position[0], target_position[1], target_position[2],
                  up[0], up[1], up[2])
    else:
        camera_position = vector_add(aircraft_position, forward, -camera_distance)
        camera_position = vector_add(camera_position, up, camera_elevation)
        camera_position = vector_add(camera_position, right, camera_lateral)
        camera_position[0] += camera_shift_x
        camera_position[1] += camera_shift_y
        camera_position[2] += camera_shift_z
        look_target = vector_add(aircraft_position, forward, 80.0)
        gluLookAt(camera_position[0], camera_position[1], camera_position[2],
                  look_target[0], look_target[1], look_target[2],
                  up[0], up[1], up[2])

def handle_keyboard(key, x, y):
    global camera_shift_x, camera_shift_y, camera_shift_z, status, projectiles, WEATHER_ACTIVE, first_person_view, show_minimap
    global barrel_roll_active, barrel_roll_angle, barrel_roll_end_time
    key_char = key.decode("utf-8").lower()
    # =========================
    # BARREL ROLL (B KEY)
    # =========================
    if key_char == 'b' and not barrel_roll_active and not status['ended']:
        barrel_roll_active = True
        barrel_roll_angle = 0.0
        status['invincibility'] = True
        barrel_roll_end_time = time.time() + BARREL_ROLL_INVINCIBLE_TIME
        print("BARREL ROLL ACTIVATED!")
    if key_char in ['u', 'U']:
        camera_shift_z += 5.0
    if key_char in ['d', 'D']:
        camera_shift_z -= 5.0
    if key_char in ['l', 'L']:
        camera_shift_x -= 5.0
    if key_char in ['r', 'R']:
        camera_shift_x += 5.0
    if key_char in ['s', 'S']:
        if status['ended']:
            restart_simulation()
            return
    if key_char == 'f':
        first_person_view = not first_person_view
        print("First person view enabled." if first_person_view else "Third person view enabled.")
    if key_char == 'm':
        show_minimap = not show_minimap
        print("Mini-map enabled." if show_minimap else "Mini-map disabled.")
    if key_char == 'p':
        status['enhanced_power'] = not status['enhanced_power']
        print("Enhanced power enabled: Press SPACE to launch projectiles." if status['enhanced_power'] else "Enhanced power disabled.")
    if key_char == 'g':
        if WEATHER_ACTIVE:
            status['invincibility'] = not status['invincibility']
            print("Invincibility enabled: Aircraft immune to weather." if status['invincibility'] else "Invincibility disabled.")
        else:
            print("Invincibility only available during weather.")
    if key_char == ' ':
        if status['enhanced_power'] and not status['ended']:
            projectile_position = list(aircraft_position)
            forward = get_forward_direction()
            projectile_position = vector_add(projectile_position, forward, 80.0)
            projectiles.append({
                'position': projectile_position,
                'direction': forward,
                'created_at': time.time() * 1000
            })
            status['hp'] -= 5.0 / 100
    if aircraft_position[2] < -300:
        aircraft_position[2] = -300
    if key_char == '\x1b':
        glutLeaveMainLoop()
    glutPostRedisplay()

def handle_special_keys(key, x, y):
    global rotation_pitch, aircraft_position
    if key == GLUT_KEY_UP:
        rotation_pitch = min(35.0, rotation_pitch + 1.8)
    if key == GLUT_KEY_DOWN:
        rotation_pitch = max(-35.0, rotation_pitch - 1.8)
    if key == GLUT_KEY_LEFT:
        aircraft_position[0] -= 15.0
    if key == GLUT_KEY_RIGHT:
        aircraft_position[0] += 15.0
    glutPostRedisplay()

def handle_mouse(button, state, x, y):
    global input_state
    if button == GLUT_LEFT_BUTTON or button == GLUT_RIGHT_BUTTON:
        if state == GLUT_DOWN:
            input_state[button] = True
        elif state == GLUT_UP:
            input_state[button] = False
    glutPostRedisplay()

def detect_collisions():
    global projectiles, obstacle_objects, collectible_objects
    if status['ended']:
        return
    aircraft_radius = 40.0
    current_timestamp = time.time() * 1000
    if status['enhanced_power']:
        destroyed_projectiles = []
        destroyed_obstacles = []
        for proj_idx, proj in enumerate(projectiles):
            proj_pos = proj['position']
            for obs_idx, obs in enumerate(obstacle_objects):
                obs_pos = obs['position']
                distance_squared = sum((proj_pos[k] - obs_pos[k]) ** 2 for k in range(3))
                obs_radius = obs['size'] * 15.0
                if distance_squared < (10.0 + obs_radius) ** 2:
                    destroyed_projectiles.append(proj_idx)
                    destroyed_obstacles.append(obs_idx)
                    status['points'] += 20
        for idx in sorted(set(destroyed_projectiles), reverse=True):
            del projectiles[idx]
        for idx in sorted(set(destroyed_obstacles), reverse=True):
            del obstacle_objects[idx]
    if not status['bonus_mode']:
        hit_obstacles = []
        for idx, obs in enumerate(obstacle_objects):
            obs_pos = obs['position']
            obs_radius = obs['size'] * 15.0
            distance_squared = sum((aircraft_position[k] - obs_pos[k]) ** 2 for k in range(3))
            if distance_squared < (aircraft_radius + obs_radius) ** 2:
                if not status['invincibility']:
                    status['hp'] -= 5 if status['enhanced_power'] else 10
                hit_obstacles.append(idx)
        for idx in sorted(hit_obstacles, reverse=True):
            del obstacle_objects[idx]
    collected_items = []
    for idx, item in enumerate(collectible_objects):
        item_pos = item['position']
        if item['category'] == 'special':
            item_radius = item['size']
            distance_squared = sum((aircraft_position[k] - item_pos[k]) ** 2 for k in range(3))
            if distance_squared < (aircraft_radius + item_radius) ** 2:
                global stored_velocity
                stored_velocity = velocity
                status['mode'] = 'Rapid Rewards'
                status['bonus_mode'] = True
                status['bonus_end'] = time.time() + 5
                global rare_collectible_present
                rare_collectible_present = False
                print("RAPID REWARDS MODE ACTIVATED!")
                collected_items.append(idx)
        else:
            item_radius = item['size'] * 8.0
            distance_squared = sum((aircraft_position[k] - item_pos[k]) ** 2 for k in range(3))
            if distance_squared < (aircraft_radius + item_radius) ** 2:
                status['points'] += 10
                collected_items.append(idx)
    for idx in sorted(collected_items, reverse=True):
        del collectible_objects[idx]
    projectiles = [proj for proj in projectiles if current_timestamp - proj['created_at'] < PROJECTILE_DURATION]

def update_entities():
    global cloud_objects, obstacle_objects, collectible_objects, projectiles, normal_collectibles_spawned, velocity
    if status['bonus_mode']:
        velocity = 50
    else:
        velocity = max(VELOCITY_MIN, min(VELOCITY_MAX, velocity))
    cloud_objects = [c for c in cloud_objects if c['position'][1] > aircraft_position[1] - 500]
    while len(cloud_objects) < CLOUD_COUNT:
        x_coord = aircraft_position[0] + random.uniform(-CLOUD_LATERAL_DIST, CLOUD_LATERAL_DIST)
        y_coord = aircraft_position[1] + CLOUD_FORWARD_DIST
        z_coord = aircraft_position[2] + random.uniform(CLOUD_HEIGHT_MIN, CLOUD_HEIGHT_MAX)
        size = random.uniform(0.5, 2.5)
        cloud_objects.append({'position': [x_coord, y_coord, z_coord], 'size': size})
    obstacle_objects = [o for o in obstacle_objects if o['position'][1] > aircraft_position[1] - 50]
    collectible_objects = [c for c in collectible_objects if c['position'][1] > aircraft_position[1] - 50]
    items_to_spawn = COLLECTIBLE_COUNT
    if status['bonus_mode']:
        items_to_spawn = COLLECTIBLE_COUNT + 1000
        obstacle_objects = []
    while len(collectible_objects) < items_to_spawn:
        x_coord = aircraft_position[0] + random.uniform(-SPAWN_LATERAL, SPAWN_LATERAL)
        y_coord = aircraft_position[1] + random.uniform(100, SPAWN_FORWARD)
        z_coord = aircraft_position[2] + random.uniform(SPAWN_HEIGHT_MIN, SPAWN_HEIGHT_MAX)
        size = random.uniform(0.5, 1.5)
        if not status['bonus_mode'] and random.random() < 0.005:
            collectible_objects.append({'position': [x_coord, y_coord, z_coord], 'size': size * 30, 'category': 'special'})
            normal_collectibles_spawned = 0
            print("Rare collectible spawned!")
        else:
            collectible_objects.append({'position': [x_coord, y_coord, z_coord], 'size': size, 'category': 'normal'})
            if not status['bonus_mode']:
                normal_collectibles_spawned += 1
    if not status['bonus_mode']:
        while len(obstacle_objects) < OBSTACLE_COUNT:
            x_coord = aircraft_position[0] + random.uniform(-SPAWN_LATERAL, SPAWN_LATERAL)
            y_coord = aircraft_position[1] + random.uniform(100, SPAWN_FORWARD)
            z_coord = aircraft_position[2] + random.uniform(SPAWN_HEIGHT_MIN, SPAWN_HEIGHT_MAX)
            size = random.uniform(0.5, 2.0)
            obstacle_objects.append({'position': [x_coord, y_coord, z_coord], 'size': size})
    current_timestamp = time.time() * 1000
    projectiles = [proj for proj in projectiles if current_timestamp - proj['created_at'] < PROJECTILE_DURATION]

def process_game_logic():
    global aircraft_position, propeller_rotation, velocity, projectiles
    global WEATHER_ACTIVE, precipitation, transitioning_weather, transition_begin, active_sky, WEATHER_START, collectible_objects
    global input_state, stored_velocity
    global barrel_roll_active, barrel_roll_angle
    global rotation_roll, status
    global FOG_ACTIVE

     # =========================
        # FOG ZONE LOGIC
     # =========================
     # Fog appears when flying low or in storm
    if aircraft_position[2] < -120 or WEATHER_ACTIVE:
     FOG_ACTIVE = True
    else:
     FOG_ACTIVE = False

    # =========================
    # BARREL ROLL ANIMATION
    # =========================
    if barrel_roll_active:
        rotation_roll += BARREL_ROLL_SPEED
        barrel_roll_angle += BARREL_ROLL_SPEED

        if barrel_roll_angle >= 360.0:
            barrel_roll_active = False
            barrel_roll_angle = 0.0
            rotation_roll = 0.0

        if time.time() > barrel_roll_end_time:
            status['invincibility'] = False

    if status['ended']:
        return
    if input_state[GLUT_LEFT_BUTTON]:
        velocity += VELOCITY_DELTA
    if input_state[GLUT_RIGHT_BUTTON]:
        velocity -= VELOCITY_DELTA
    was_bonus_active = status['bonus_mode']
    if status['bonus_mode'] and time.time() > status['bonus_end']:
        status['mode'] = 'Obstacle Run'
        status['bonus_mode'] = False
        velocity = stored_velocity
        print("BONUS MODE ENDED. Returning to normal gameplay.")
    is_bonus_active_now = status['bonus_mode']
    if was_bonus_active and not is_bonus_active_now:
        collectible_objects = []
    if WEATHER_ACTIVE and not status['invincibility']:
        status['hp'] -= 0.02
    if status['hp'] <= 0:
        status['ended'] = True
        print("Game Over! Aircraft destroyed.")
        print(f"Final Score: {status['points']}")
    if status['mode'] == 'Time Trial':
        elapsed = time.time() - status['init_time']
        if elapsed > status['time_limit']:
            status['ended'] = True
            print("Game Over! Time expired.")
            print(f"Final Score: {status['points']}")
    forward = get_forward_direction()
    aircraft_position = vector_add(aircraft_position, forward, velocity)
    for proj in projectiles:
        proj['position'] = vector_add(proj['position'], proj['direction'], PROJECTILE_VELOCITY)
    detect_collisions()
    update_entities()
    propeller_rotation = (propeller_rotation + 30) % 360
    current_time = time.time()
    new_weather_state = (current_time - WEATHER_START) % (WEATHER_CYCLE + WEATHER_LENGTH) < WEATHER_LENGTH
    if new_weather_state != WEATHER_ACTIVE:
        transitioning_weather = True
        transition_begin = current_time
        WEATHER_ACTIVE = new_weather_state
    if transitioning_weather:
        progress = (current_time - transition_begin) / transition_time
        progress = min(progress, 1.0)
        start_color = storm_sky if not WEATHER_ACTIVE else clear_sky
        end_color = clear_sky if not WEATHER_ACTIVE else storm_sky
        active_sky = [
            start_color[i] * (1 - progress) + end_color[i] * progress for i in range(3)
        ]
        if progress >= 1.0:
            transitioning_weather = False
            if not WEATHER_ACTIVE:
                status['invincibility'] = False
                print("Invincibility disabled as weather cleared.")
    if WEATHER_ACTIVE and not precipitation:
        precipitation = []
        for _ in range(PRECIPITATION_COUNT):
            angle = random.uniform(0, 2 * math.pi)
            x_coord = aircraft_position[0] + PRECIPITATION_AREA * math.cos(angle)
            y_coord = aircraft_position[1] + PRECIPITATION_AREA * math.sin(angle)
            z_coord = random.uniform(aircraft_position[2] + PRECIPITATION_ALTITUDE / 2, aircraft_position[2] - PRECIPITATION_ALTITUDE / 2)
            precipitation.append([x_coord, y_coord, z_coord])
    if WEATHER_ACTIVE:
        for droplet in precipitation:
            droplet[2] -= PRECIPITATION_FALL_RATE
            if droplet[2] < aircraft_position[2] - PRECIPITATION_ALTITUDE / 2:
                angle = random.uniform(0, 2 * math.pi)
                droplet[0] = aircraft_position[0] + PRECIPITATION_AREA * math.cos(angle)
                droplet[1] = aircraft_position[1] + PRECIPITATION_AREA * math.sin(angle)
                droplet[2] = aircraft_position[2] + PRECIPITATION_ALTITUDE / 2

def idle_callback():
    process_game_logic()
    glutPostRedisplay()

def enable_fog():
    glEnable(GL_FOG)
    glFogi(GL_FOG_MODE, GL_LINEAR)
    glFogfv(GL_FOG_COLOR, FOG_COLOR)
    glFogf(GL_FOG_START, FOG_START)
    glFogf(GL_FOG_END, FOG_END)
    glHint(GL_FOG_HINT, GL_NICEST)

def disable_fog():
    glDisable(GL_FOG)


def render_scene():
    global active_sky, transitioning_weather, WEATHER_ACTIVE
    glClearColor(active_sky[0], active_sky[1], active_sky[2], 1.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    configure_camera()
    if FOG_ACTIVE:
     enable_fog()
    else:
     disable_fog()
    render_sky_background()
    if barrel_roll_active:
     render_text_overlay(
        WINDOW_WIDTH / 2 - 80,
        WINDOW_HEIGHT - 80,
        "BARREL ROLL!",
        font_type=GLUT_BITMAP_TIMES_ROMAN_24,
        text_color=(0.0, 0.6, 1.0)
    )

    if FOG_ACTIVE:
     render_text_overlay(
        10, 470,
        "FOG ZONE",
        font_type=GLUT_BITMAP_TIMES_ROMAN_24,
        text_color=(0.4, 0.4, 0.4)
    )

    
    if WEATHER_ACTIVE or transitioning_weather:
        glPushMatrix()
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glDepthMask(GL_FALSE)
        glColor4f(0.7, 0.8, 1.0, 0.6)
        glLineWidth(2.0)
        glBegin(GL_LINES)
        for droplet in precipitation:
            glVertex3f(droplet[0], droplet[1], droplet[2])
            glVertex3f(droplet[0], droplet[1], droplet[2] - 100)
        glEnd()
        glDepthMask(GL_TRUE)
        glDisable(GL_BLEND)
        glPopMatrix()
    for proj in projectiles:
        glPushMatrix()
        glTranslatef(*proj['position'])
        render_projectile_shape()
        glPopMatrix()
    for obs in obstacle_objects:
        glPushMatrix()
        glTranslatef(*obs['position'])
        glScalef(obs['size'], obs['size'], obs['size'])
        render_obstacle_shape()
        glPopMatrix()
    for item in collectible_objects:
        glPushMatrix()
        glTranslatef(*item['position'])
        glScalef(item['size'], item['size'], item['size'])
        render_collectible_item(rare=(item['category'] == 'special'))
        glPopMatrix()
    if not (WEATHER_ACTIVE or transitioning_weather):
        render_all_clouds()
    if not first_person_view:
        render_aircraft()
    
    # Render minimap last (on top of everything)
    render_minimap()
    
    glColor3f(0.0, 0.0, 0.0)
    render_text_overlay(10, 680, f"Adventure Level: {status['mode']}")
    render_text_overlay(10, 650, f"Speed: {velocity:.1f}")
    render_text_overlay(10, 620, f"Health: {status['hp']:.1f} HP",
                      text_color=(1, 0, 0) if status['hp'] < 30 else (0, 0, 0))
    render_text_overlay(10, 590, f"Score: {status['points']}")
    if status['mode'] == 'Time Trial':
        elapsed = time.time() - status['init_time']
        if elapsed > status['time_limit']:
            status['ended'] = True
            print("Game Over! Time expired.")
            print(f"Final Score: {status['points']}")
    if status['enhanced_power']:
        render_text_overlay(10, 530, "POWER MODE ON",
              font_type=GLUT_BITMAP_TIMES_ROMAN_24, text_color=(1, 0, 0))
    if status['invincibility']:
        render_text_overlay(10, 500, "GHOST MODE ON",
              font_type=GLUT_BITMAP_TIMES_ROMAN_24, text_color=(0, 1, 0))
    if status['bonus_mode']:
        remaining_time = max(0, status['bonus_end'] - time.time())
        render_text_overlay(WINDOW_WIDTH/2 - 120, WINDOW_HEIGHT/2, f"RAPID REWARDS: {remaining_time:.1f}s", font_type=GLUT_BITMAP_TIMES_ROMAN_24, text_color=(0, 0.8, 0.0))
    if first_person_view:
        render_text_overlay(10, 560, "FIRST PERSON MODE", text_color=(0.5, 0.5, 0.5))
    else:
        render_text_overlay(10, 560, "THIRD PERSON MODE", text_color=(0.5, 0.5, 0.5))
    if status['ended']:
        render_text_overlay(WINDOW_WIDTH / 2 - 100, WINDOW_HEIGHT / 2, "GAME OVER",
                      font_type=GLUT_BITMAP_TIMES_ROMAN_24, text_color=(0, 0, 0))
        render_text_overlay(WINDOW_WIDTH / 2 - 100, WINDOW_HEIGHT / 2 - 50, f"FINAL SCORE: {status['points']}",
                      font_type=GLUT_BITMAP_TIMES_ROMAN_24, text_color=(0, 0, 0))
        render_text_overlay(WINDOW_WIDTH / 2 - 200, WINDOW_HEIGHT / 2 - 100, "Press 'S' or 's' to restart the game",
                      font_type=GLUT_BITMAP_TIMES_ROMAN_24, text_color=(0, 0, 0))
    glutSwapBuffers()

def populate_clouds():
    global cloud_objects
    cloud_objects = []
    for _ in range(CLOUD_COUNT):
        x_coord = random.uniform(-CLOUD_LATERAL_DIST, CLOUD_LATERAL_DIST)
        y_coord = random.uniform(0, CLOUD_FORWARD_DIST)
        z_coord = random.uniform(CLOUD_HEIGHT_MIN, CLOUD_HEIGHT_MAX)
        size = random.uniform(0.5, 2.5)
        cloud_objects.append({'position': [x_coord, y_coord, z_coord], 'size': size})

def populate_obstacles_collectibles():
    global obstacle_objects, collectible_objects, rare_collectible_present
    rare_collectible_present = False
    obstacle_objects = []
    collectible_objects = []
    for _ in range(OBSTACLE_COUNT):
        x_coord = random.uniform(-SPAWN_LATERAL, SPAWN_LATERAL)
        y_coord = random.uniform(0, SPAWN_FORWARD)
        z_coord = random.uniform(SPAWN_HEIGHT_MIN, SPAWN_HEIGHT_MAX)
        size = random.uniform(0.5, 2.0)
        obstacle_objects.append({'position': [x_coord, y_coord, z_coord], 'size': size})
    for _ in range(COLLECTIBLE_COUNT):
        x_coord = random.uniform(-SPAWN_LATERAL, SPAWN_LATERAL)
        y_coord = random.uniform(0, SPAWN_FORWARD)
        z_coord = random.uniform(SPAWN_HEIGHT_MIN, SPAWN_HEIGHT_MAX)
        size = random.uniform(0.5, 1.5)
        is_rare = random.random() < RARE_COLLECTIBLE_CHANCE and not rare_collectible_present
        if is_rare:
            rare_collectible_present = True
        collectible_objects.append({'position': [x_coord, y_coord, z_coord], 'size': size, 'category': 'special' if is_rare else 'normal'})

def initialize_program():
    global quadric_object, status
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(WINDOW_WIDTH, WINDOW_HEIGHT)
    glutCreateWindow(b"Sky Adventure")
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glClearColor(0.5, 0.7, 1.0, 1.0)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glEnable(GL_LINE_SMOOTH)
    glEnable(GL_POINT_SMOOTH)
    glEnable(GL_POLYGON_SMOOTH)
    glShadeModel(GL_SMOOTH)
    quadric_object = gluNewQuadric()
    populate_clouds()
    populate_obstacles_collectibles()
    status['init_time'] = time.time()
    glutDisplayFunc(render_scene)
    glutKeyboardFunc(handle_keyboard)
    glutSpecialFunc(handle_special_keys)
    glutMouseFunc(handle_mouse)
    glutIdleFunc(idle_callback)
    glutMainLoop()

if __name__ == "__main__":
    initialize_program()