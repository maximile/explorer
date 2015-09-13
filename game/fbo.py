import pyglet
import pyglet.gl
import ctypes


class FBO(object):
    """Basic helper for using OpenGL's Frame Buffer Object (FBO)"""

    def __init__(self, width, height):
        """Creates a Frame Buffer Object (FBO)"""
    
        # Must be supported...
        assert pyglet.gl.gl_info.have_extension("GL_EXT_framebuffer_object")
        assert pyglet.gl.gl_info.have_extension("GL_ARB_draw_buffers")
        
        self.width = width
        self.height = height
        self.tex_width = next_power_of_two(width)
        self.tex_height = next_power_of_two(height)
 
        # Setting it up
        self.framebuffer = ctypes.c_uint(0)
        self.img = ctypes.c_uint(0)
        
        pyglet.gl.glGenFramebuffersEXT(1, ctypes.byref(self.framebuffer))
        pyglet.gl.glBindFramebufferEXT(pyglet.gl.GL_FRAMEBUFFER_EXT,
                                       self.framebuffer)
            
        # Adding a Texture To Render To
        pyglet.gl.glGenTextures(1, ctypes.byref(self.img))
        pyglet.gl.glBindTexture(pyglet.gl.GL_TEXTURE_2D, self.img)
    
        # Use nearest-neighbour filtering
        pyglet.gl.glTexParameteri(pyglet.gl.GL_TEXTURE_2D,
                                  pyglet.gl.GL_TEXTURE_MAG_FILTER,
                                  pyglet.gl.GL_NEAREST)
        pyglet.gl.glTexParameteri(pyglet.gl.GL_TEXTURE_2D,
                                  pyglet.gl.GL_TEXTURE_MIN_FILTER,
                                  pyglet.gl.GL_NEAREST)

        # Add the texture ot the frame buffer as a color buffer
        pyglet.gl.glTexImage2D(pyglet.gl.GL_TEXTURE_2D, 0, pyglet.gl.GL_RGBA8,
                               self.tex_width, self.tex_height, 0, pyglet.gl.GL_RGBA,
                               pyglet.gl.GL_UNSIGNED_BYTE, None)
        pyglet.gl.glFramebufferTexture2DEXT(pyglet.gl.GL_FRAMEBUFFER_EXT,
                                            pyglet.gl.GL_COLOR_ATTACHMENT0_EXT,
                                            pyglet.gl.GL_TEXTURE_2D, self.img, 0)
    
        # Check if it worked so far
        status = pyglet.gl.glCheckFramebufferStatusEXT(
            pyglet.gl.GL_FRAMEBUFFER_EXT)
        assert status == pyglet.gl.GL_FRAMEBUFFER_COMPLETE_EXT

    def attach(self):
        """Call this before rendering to the FBO."""

        # First we bind the FBO so we can render to it
        pyglet.gl.glBindFramebufferEXT(pyglet.gl.GL_FRAMEBUFFER_EXT,
                                       self.framebuffer)
        
        # Save the view port and set it to the size of the texture
        # pyglet.gl.glPushAttrib(pyglet.gl.GL_VIEWPORT_BIT)
        # pyglet.gl.glViewport(0, 0, self.width, self.height)

    def detach(self):
        """Call this after rendering to the FBO so that rendering now
        goes to the regular frame buffer."""

        # Restore old view port and set rendering back to default frame buffer
        # pyglet.gl.glPopAttrib()
        pyglet.gl.glBindFramebufferEXT(pyglet.gl.GL_FRAMEBUFFER_EXT, 0)

    def get_texture(self):
        """Returns a pyglet image with the contents of the FBO."""
        self.data = (ctypes.c_ubyte * (self.width * self.height * 4))()

        pyglet.gl.glGetTexImage(pyglet.gl.GL_TEXTURE_2D, 0,
                                pyglet.gl.GL_RGBA, pyglet.gl.GL_UNSIGNED_BYTE,
                                self.data)

        return pyglet.image.ImageData(self.width, self.height,
                                      'RGBA', self.data)
        
    def __del__(self):
        """Deallocates memory. Call this before discarding FBO."""
        pyglet.gl.glDeleteFramebuffersEXT(1, ctypes.byref(self.framebuffer))
        pyglet.gl.glDeleteTextures(1, ctypes.byref(self.img))


def next_power_of_two(value):
    test_pot = 2
    while True:
        if value <= test_pot:
            return test_pot
        test_pot *= 2
        if test_pot > 16384:
            raise ValueError("Too big: %i" % value)
