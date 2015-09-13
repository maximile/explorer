import ctypes
import pyglet

LEFT = -1, 0
RIGHT = 1, 0
UP = 0, 1
DOWN = 0, -1

FACING_LEFT = "FACING_LEFT"
FACING_RIGHT = "FACING_RIGHT"
GEAR_DOWN = "GEAR_DOWN"
GEAR_UP = "GEAR_UP"


class Player(object):
    def __init__(self):
        # Images and collision masks:
        image_paths_for_states = {
            (FACING_RIGHT, GEAR_UP): "images/car_right_up.png",
            (FACING_RIGHT, GEAR_DOWN): "images/car_right_down.png",
            (FACING_LEFT, GEAR_UP): "images/car_left_up.png",
            (FACING_LEFT, GEAR_DOWN): "images/car_left_down.png"
        }
        
        self._sprites = {}
        self._collision_masks = {}
        self.width = None
        self.height = None
        self.landed = False
        for state, image_path in image_paths_for_states.items():
            # Sprite:
            image = pyglet.image.load(image_path)
            self._sprites[state] = pyglet.sprite.Sprite(image)
            
            # Collision data
            alpha_data = image.get_image_data().get_data("A", image.width)
            mask = tuple([ord(d) > 127 for d in alpha_data])
            self._collision_masks[state] = mask
            
            # Check dimensions match
            if self.width is None:
                self.width = image.width
            elif not self.width == image.width:
                raise ValueError("Widths don't match.")
            if self.height is None:
                self.height = image.height
            elif not self.height == image.height:
                raise ValueError("Widths don't match.")
        
        self.facing = FACING_RIGHT
        self.vel = 0.0, 0.0
        self.pos = 50.0, 50.0
        self.gear_state = GEAR_UP
        self.inputs = {LEFT: False, RIGHT: False, UP: False, DOWN: False}
        
        self.engine_player = pyglet.media.Player()
        self.engine_sound = pyglet.media.load("sounds/engine.wav", streaming=False)
        self.land_sound = pyglet.media.load("sounds/land.wav", streaming=False)
        self.crash_sound = pyglet.media.load("sounds/crash.wav", streaming=False)
    
    def can_land(self):
        return self.gear_state == GEAR_DOWN
    
    def land(self):
        self.land_sound.play()
        if not self.can_land():
            self.crash()
        self.vel = 0.0, 0.0
        self.pos = self.pos[0], self.pos[1] + 1
        self.landed = True
    
    def crash(self):
        self.pos = 50.0, 50.0
        self.vel = 0.0, 0.0
        self.gear_state = GEAR_UP
        self.landed = False
        self.crash_sound.play()
    
    def take_off(self):
        self.gear_state = GEAR_UP
        self.landed = False
    
    def toggle_gear(self):
        self.landed = False
        if self.gear_state == GEAR_DOWN:
            self.gear_state = GEAR_UP
        else:
            self.gear_state = GEAR_DOWN
    
    @property
    def collision_mask(self):
        state = self.facing, self.gear_state
        return self._collision_masks[state]
    
    def update(self, dt):
        if self.landed:
            return
        thrust = 2.6
        accel = 0.0, -0.35
        for direction in LEFT, RIGHT, UP, DOWN:
            if not self.inputs[direction]:
                continue
            if direction in [LEFT, RIGHT] and self.gear_state == GEAR_DOWN:
                continue
            accel = (accel[0] + direction[0] * thrust,
                     accel[1] + direction[1] * thrust)
        self.vel = self.vel[0] + accel[0], self.vel[1] + accel[1]
        self.pos = (self.pos[0] + self.vel[0] * dt,
                    self.pos[1] + self.vel[1] * dt)
        
        # Engine sound
        should_play_sound = False
        if (not self.inputs[LEFT] == self.inputs[RIGHT] or
                not self.inputs[UP] == self.inputs[DOWN]):
            if not self.landed:
                should_play_sound = True
        if should_play_sound:
            if not self.engine_player.source:
                self.engine_player.queue(self.engine_sound)
            if not self.engine_player.playing:
                self.engine_player.seek(0.0)
                self.engine_player.play()
        else:
            self.engine_player.pause()

    def direction_pressed(self, direction):
        if not self.landed:
            if direction == LEFT:
                self.facing = FACING_LEFT
            if direction == RIGHT:
                self.facing = FACING_RIGHT
        
        if not direction in self.inputs:
            raise ValueError(direction)
        self.inputs[direction] = True
    
    def direction_released(self, direction):
        if not direction in self.inputs:
            raise ValueError(direction)
        self.inputs[direction] = False
    
    def draw(self):
        state = self.facing, self.gear_state
        sprite = self._sprites[state]
        sprite.x = self.pos[0]
        sprite.y = self.pos[1]
        sprite.draw()
