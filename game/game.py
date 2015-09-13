import os
import pyglet

import level
import player

class Game(object):
    def __init__(self):
        self.level = level.Level(0, 0)
        self.player = player.Player()
        self.player.pos = self.level.nearest_checkpoint(0, 0)
        self.rescued_mans = {}
    
    def update(self, dt):
        self.player.update(dt)
        
        # Check for collision
        level_mask = self.level.collision_mask
        player_mask = self.player.collision_mask
        
        # Number of bottom-row collisions required for a safe landing
        bottom_row = player_mask[:self.player.width]
        required_bottom_row_collisions = bottom_row.count(True)
        
        bottom_row_collisions = 0
        other_collisions = 0
        for y in xrange(self.player.height):
            for x in xrange(self.player.width):
                player_val = player_mask[y * self.player.width + x]
                level_x = x + int(self.player.pos[0])
                level_y = y + int(self.player.pos[1])
                if level_x < 0 or level_x >= self.level.width:
                    continue
                if level_y < 0 or level_y >= self.level.height:
                    continue
                level_val = level_mask[level_y * self.level.width + level_x]
                # print level_val, player_val
                if level_val and player_val:
                    if y == 0:
                        bottom_row_collisions += 1
                    else:
                        other_collisions += 1
        
        if (bottom_row_collisions == required_bottom_row_collisions and
                not other_collisions and self.player.can_land()):
            self.player.land()
        elif other_collisions or bottom_row_collisions:
            self.player.crash()
        
        # Mans to rescue?
        for key, the_man in self.level.mans.items():
            door_pos = (self.player.pos[0] + self.player.width // 2,
                        self.player.pos[1])
            dist = ((the_man.pos[0] - door_pos[0]) ** 2 +
                    (the_man.pos[1] - door_pos[1]) ** 2) ** 0.5
            if dist < 5:
                del self.level.mans[key]
                rescued = self.rescued_mans.setdefault(self.level.coords, [])
                rescued.append(key)
            
        # Handle leaving screen. Harmless collision if no connection:
        if self.player.pos[1] < 0 and not level.BOTTOM in self.level.connections:
            self.player.pos = self.player.pos[0], 0
            self.player.vel = self.player.vel[0], 0
        if self.player.pos[0] < 0 and not level.LEFT in self.level.connections:
            self.player.pos = 0, self.player.pos[1]
            self.player.vel = 0, self.player.vel[1]
        if (self.player.pos[0] + self.player.width > self.level.width and
                not level.RIGHT in self.level.connections):
            self.player.pos = self.level.width - self.player.width, self.player.pos[1]
            self.player.vel = 0, self.player.vel[1]
        if (self.player.pos[1] + self.player.height > self.level.height and
                not level.TOP in self.level.connections):
            self.player.pos = self.player.pos[0], self.level.height - self.player.height
            self.player.vel = self.player.vel[0], 0
        
        # Warp if there's a connection
        if (self.player.pos[0] + self.player.width < 0 and
                level.LEFT in self.level.connections):
            self.warp_to(level.LEFT)
        if (self.player.pos[0] > self.level.width and
                level.RIGHT in self.level.connections):
            self.warp_to(level.RIGHT)
        if (self.player.pos[1] + self.player.height < 0 and
                level.BOTTOM in self.level.connections):
            self.warp_to(level.BOTTOM)
        if (self.player.pos[1] > self.level.height and
                level.TOP in self.level.connections):
            self.warp_to(level.TOP)

    def warp_to(self, direction):
        self.player.vel = 0, 0
        if direction == level.LEFT:
            coords = self.level.coords[0] - 1, self.level.coords[1]
        elif direction == level.RIGHT:
            coords = self.level.coords[0] + 1, self.level.coords[1]
        elif direction == level.TOP:
            coords = self.level.coords[0], self.level.coords[1] + 1
        elif direction == level.BOTTOM:
            coords = self.level.coords[0], self.evel.coords[1] - 1
            
        self.level = level.Level(coords[0], coords[1],
                                 rescued_mans=self.rescued_mans.get(coords, []))
        
        if direction == level.LEFT:
            self.player.pos = self.level.nearest_checkpoint(self.level.width,
                                                            self.player.pos[1])
        elif direction == level.RIGHT:
            self.player.pos = self.level.nearest_checkpoint(0,
                                                            self.player.pos[1])
        elif direction == level.TOP:
            self.player.pos = self.level.nearest_checkpoint(self.player.pos[0],
                                                            0)
        elif direction == level.BOTTOM:
            self.player.pos = self.level.nearest_checkpoint(self.player.pos[0],
                                                            self.level.height)
        
        if self.level.bg_col == (0, 0, 0):
            self.player.color = player.WHITE
        else:
            self.player.color = player.BLACK
    
    def key_pressed(self, symbol, modifiers):
        # Quit:
        if (symbol == pyglet.window.key.Q and
                modifiers == pyglet.window.key.MOD_COMMAND):
            os._exit(0)
        
        # Space
        if symbol == pyglet.window.key.SPACE:
            self.player.toggle_gear()
        
        # Arrow keys
        dirs_for_symbols = {pyglet.window.key.LEFT: (-1, 0),
                            pyglet.window.key.RIGHT: (1, 0),
                            pyglet.window.key.UP: (0, 1),
                            pyglet.window.key.DOWN: (0, -1)}
        if symbol in dirs_for_symbols:
            self.player.direction_pressed(dirs_for_symbols[symbol])
        
        if symbol == pyglet.window.key.UP and self.player.landed:
            self.player.take_off()

    def key_released(self, symbol, modifiers):
        # Arrow keys
        dirs_for_symbols = {pyglet.window.key.LEFT: (-1, 0),
                            pyglet.window.key.RIGHT: (1, 0),
                            pyglet.window.key.UP: (0, 1),
                            pyglet.window.key.DOWN: (0, -1)}
        if symbol in dirs_for_symbols:
            self.player.direction_released(dirs_for_symbols[symbol])
    
    def draw(self):
        self.level.draw()
        self.player.draw()
