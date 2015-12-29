import pyglet

import fbo


class GameWindow(pyglet.window.Window):
    def __init__(self, game):
        w = game.level.width * 2
        h = game.level.height * 2
        super(GameWindow, self).__init__(w, h, resizable=True)
        self.game = game
    
    def on_key_press(self, symbol, modifiers):
        self.game.key_pressed(symbol, modifiers)

    def on_key_release(self, symbol, modifiers):
        self.game.key_released(symbol, modifiers)
    
    def on_draw(self):
        self.fbo = fbo.FBO(self.game.level.width,
                           self.game.level.height)
        self.fbo.attach()
        pyglet.gl.glColor3f(1.0, 0.0, 0.0)
        # self.clear()
        pyglet.gl.glClearColor(0.0, 1.0, 1.0, 1.0)
        pyglet.gl.glClear(pyglet.gl.GL_COLOR_BUFFER_BIT)
        pyglet.gl.glLoadIdentity()
        self.game.draw()
        pyglet.gl.glFlush()
        self.fbo.detach()
        pyglet.gl.glClearColor(0.0, 0.0, 0.0, 1.0)

        pyglet.gl.glColor3f(1.0, 1.0, 1.0)

        pyglet.gl.glLoadIdentity()

        # Set up xform matrix so level is centered in window. Scale so it
        # nearly fits:
        required_pixels = (self.fbo.width,
                           self.fbo.height)
        x_scale = self.width // required_pixels[0]
        y_scale = self.height // required_pixels[1]
        scale = min(x_scale, y_scale)
        pyglet.gl.glScalef(scale, scale, scale)

        # Then transform so it's centered
        offset_x = (self.width - (required_pixels[0] * scale)) // 2
        offset_y = (self.height - (required_pixels[1] * scale)) // 2
        pyglet.gl.glTranslatef(offset_x // scale, offset_y // scale, 0.0)

        self.clear()
        
        pyglet.gl.glBindTexture(pyglet.gl.GL_TEXTURE_2D, self.fbo.img)
        pyglet.gl.glEnable(pyglet.gl.GL_TEXTURE_2D)
        
        verts = [(0.0, 0.0),
                 (self.fbo.width, 0.0),
                 (self.fbo.width, self.fbo.height),
                 (0.0, self.fbo.height)]
        tex_coords = [(0.0, 0.0),
                      (self.fbo.width / float(self.fbo.tex_width), 0.0),
                      (self.fbo.width / float(self.fbo.tex_width),
                       self.fbo.height / float(self.fbo.tex_height)),
                      (0.0, self.fbo.height / float(self.fbo.tex_height))]
        
        pyglet.gl.glBegin(pyglet.gl.GL_QUADS)
        for vc, tc in zip(verts, tex_coords):
            pyglet.gl.glTexCoord2f(*tc)
            pyglet.gl.glVertex2f(*vc)
        pyglet.gl.glEnd()
