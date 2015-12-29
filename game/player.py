import copy
import pyglet

import color
import pixmap

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
        car_path = "images/car.png"
        car_image = pyglet.image.load(car_path)
        car_pixmap = pixmap.Pixmap.from_pyglet_image(car_image)
        pixmap_gear_down = copy.deepcopy(car_pixmap)
        pixmap_gear_down.remove_colors(keep=[color.BLACK, color.TRANSPARENT])
        pixmap_gear_up = copy.deepcopy(car_pixmap)
        pixmap_gear_down.remove_colors(
            keep=[color.BLACK, color.GREEN, color.TRANSPARENT])
        pixmap_gear_down.replace_colors({color.GREEN: color.BLACK})
        
        states = [(FACING_RIGHT, GEAR_UP, color.BLACK),
                  (FACING_RIGHT, GEAR_DOWN, color.BLACK),
                  (FACING_LEFT, GEAR_UP, color.BLACK),
                  (FACING_LEFT, GEAR_DOWN, color.BLACK),
                  (FACING_RIGHT, GEAR_UP, color.WHITE),
                  (FACING_RIGHT, GEAR_DOWN, color.WHITE),
                  (FACING_LEFT, GEAR_UP, color.WHITE),
                  (FACING_LEFT, GEAR_DOWN, color.WHITE)]
        
        pixmaps_for_states = {}
        for facing, gear, col in states:
            if gear == GEAR_DOWN:
                pix_map = copy.deepcopy(pixmap_gear_down)
            else:
                pix_map = copy.deepcopy(pixmap_gear_up)
            if facing == FACING_LEFT:
                pix_map.flip()
            if col == color.WHITE:
                pix_map.invert()
            pixmaps_for_states[facing, gear, col] = pix_map
        
        # # Get thruster images
        # thrusters_pixmap = pix_map
        
        self._sprites = {}
        self._collision_maps = {}
        self.width = None
        self.height = None
        self.landed = False
        self.color = color.BLACK
        for state, pix_map in pixmaps_for_states.items():
            # Sprite:
            image = pix_map.to_image()
            self._sprites[state] = pyglet.sprite.Sprite(image)
            
            # Collision data
            self._collision_maps[state] = pix_map
            
            # Check dimensions match
            if self.width is None:
                self.width = image.width
            elif not self.width == image.width:
                raise ValueError("Widths don't match.")
            if self.height is None:
                self.height = image.height
            elif not self.height == image.height:
                raise ValueError("Widths don't match.")
        
        # Get rects containing thruster images
        thrusters_pixmap = copy.deepcopy(car_pixmap)
        thrusters_pixmap.remove_colors(keep=[color.RED, color.TRANSPARENT])
        thrusters_pixmap.replace_colors({color.RED: color.BLACK})
        rects = thrusters_pixmap.get_sub_rects(color.BLACK, threshold=2)
        if not len(rects) == 4:
            raise RuntimeError("Expected four red sprites in %s" % car_path)
        
        # Get one for each direction
        thruster_rects = {LEFT: rects[0], RIGHT: rects[0],
                          UP: rects[0], DOWN: rects[0]}
        for rect in rects:
            if rect.center[0] < thruster_rects[LEFT].center[0]:
                thruster_rects[LEFT] = rect
            if rect.center[0] > thruster_rects[RIGHT].center[0]:
                thruster_rects[RIGHT] = rect
            if rect.center[1] < thruster_rects[UP].center[1]:
                thruster_rects[UP] = rect
            if rect.center[1] > thruster_rects[DOWN].center[1]:
                thruster_rects[DOWN] = rect
                
        self._thruster_sprites = {}
        for direction, rect in thruster_rects.items():
            pix_map = copy.deepcopy(thrusters_pixmap)
            pix_map.fill_rect(rect.x, rect.y, rect.width, rect.height,
                              color.TRANSPARENT, invert=True)
            self._thruster_sprites[direction, FACING_RIGHT, color.BLACK] = (
                pyglet.sprite.Sprite(pix_map.to_image()))
            pix_map.flip()
            self._thruster_sprites[direction, FACING_LEFT, color.BLACK] = (
                pyglet.sprite.Sprite(pix_map.to_image()))
            pix_map.flip()
            pix_map.replace_colors({color.BLACK: color.WHITE})
            self._thruster_sprites[direction, FACING_RIGHT, color.WHITE] = (
                pyglet.sprite.Sprite(pix_map.to_image()))
            pix_map.flip()
            self._thruster_sprites[direction, FACING_LEFT, color.WHITE] = (
                pyglet.sprite.Sprite(pix_map.to_image()))
        
        self.facing = FACING_RIGHT
        self.vel = 0.0, 0.0
        self.pos = 50.0, 50.0
        self.gear_state = GEAR_UP
        self.inputs = {LEFT: False, RIGHT: False, UP: False, DOWN: False}
        
        self.engine_player = pyglet.media.Player()
        self.engine_sound = pyglet.media.load("sounds/engine.wav", streaming=False)
        self.land_sound = pyglet.media.load("sounds/land.wav", streaming=False)
        self.crash_sound = pyglet.media.load("sounds/crash.wav", streaming=False)
        
        # # Thruster sprites
        # self.thruster_sprites = {}
        # paths_for_cols = {color.WHITE: "images/thrusters_white.png",
        #                   color.BLACK: "images/thrusters.png"}
        # for col, path in paths_for_cols.items():
        #     self.thruster_sprites[col] = {}
        #     thruster_img = pyglet.image.load(path)
        #     thruster_grid = pyglet.image.ImageGrid(thruster_img, 2, 4)
        #     cols_dirs = LEFT, UP, RIGHT, DOWN
        #     for column, direction in enumerate(cols_dirs):
        #         frames = thruster_grid[0, column], thruster_grid[1, column]
        #         anim = pyglet.image.Animation.from_image_sequence(frames, 0.3, True)
        #         self.thruster_sprites[col][direction] = pyglet.sprite.Sprite(anim)
    
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
    def collision_map(self):
        state = self.facing, self.gear_state, self.color
        return self._collision_maps[state]
    
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
        state = self.facing, self.gear_state, self.color
        sprite = self._sprites[state]
        sprite.x = self.pos[0]
        sprite.y = self.pos[1]
        sprite.draw()
        
        for direction, value in self.inputs.items():
            if not value:
                continue
            sprite = self._thruster_sprites[direction, self.facing, self.color]
            sprite.x = self.pos[0]
            sprite.y = self.pos[1]
            sprite.draw()
