import os
import pyglet

import level
import player


class Game(object):
    def __init__(self):
        self.level = level.Level("images/tetris.psd")
        self.player = player.Player()
        print self.level.nearest_checkpoint(0, 0)
        self.player.pos = self.level.nearest_checkpoint(0, 0)
    
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
                if level_x < 0 or level_x > self.level.width:
                    continue
                if level_y < 0 or level_y > self.level.height:
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
