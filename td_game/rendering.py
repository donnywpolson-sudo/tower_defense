from dataclasses import dataclass
import struct

import pygame


@dataclass
class RenderOptions:
    renderer: str = "pygame"
    enable_glow: bool = True
    enable_particles: bool = True
    enable_screen_shake: bool = True
    max_particles: int = 450


class PygameRenderer:
    name = "pygame"

    def __init__(self, size, caption):
        self.width, self.height = size
        self.window = pygame.display.set_mode(size, pygame.RESIZABLE)
        pygame.display.set_caption(caption)

    @property
    def window_size(self):
        surface = pygame.display.get_surface()
        if surface:
            self.width, self.height = surface.get_size()
        return self.width, self.height

    def resize(self, size):
        self.width, self.height = size

    def present(self, surface, scale, offset_x, offset_y, shake_x=0, shake_y=0, enable_glow=False):
        self.window = pygame.display.get_surface() or self.window
        self.window.fill((12, 14, 12))
        draw_width = max(1, int(surface.get_width() * scale))
        draw_height = max(1, int(surface.get_height() * scale))
        scaled_screen = pygame.transform.smoothscale(surface, (draw_width, draw_height))
        self.window.blit(scaled_screen, (offset_x + shake_x, offset_y + shake_y))
        pygame.display.flip()

    def close(self):
        pass


class OpenGLRenderer:
    name = "opengl"

    def __init__(self, size, caption):
        import moderngl

        self.moderngl = moderngl
        self.width, self.height = size
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 3)
        pygame.display.gl_set_attribute(pygame.GL_DOUBLEBUFFER, 1)
        pygame.display.set_mode(size, pygame.OPENGL | pygame.DOUBLEBUF | pygame.RESIZABLE)
        pygame.display.set_caption(caption)

        self.ctx = moderngl.create_context()
        self.ctx.enable(moderngl.BLEND)
        self.ctx.blend_func = moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA
        self.texture = self.ctx.texture(size, 4)
        self.texture.filter = (moderngl.LINEAR, moderngl.LINEAR)
        self.texture.repeat_x = False
        self.texture.repeat_y = False

        self.program = self.ctx.program(
            vertex_shader="""
                #version 330
                in vec2 in_pos;
                in vec2 in_uv;
                out vec2 v_uv;

                void main() {
                    gl_Position = vec4(in_pos, 0.0, 1.0);
                    v_uv = in_uv;
                }
            """,
            fragment_shader="""
                #version 330
                uniform sampler2D game_texture;
                uniform float glow_enabled;
                in vec2 v_uv;
                out vec4 frag_color;

                void main() {
                    vec4 color = texture(game_texture, v_uv);
                    if (glow_enabled > 0.5) {
                        float bright = max(max(color.r, color.g), color.b);
                        float glow = smoothstep(0.55, 1.0, bright) * 0.18;
                        color.rgb += color.rgb * glow;
                    }
                    frag_color = color;
                }
            """,
        )
        self.program["game_texture"].value = 0
        self.vbo = self.ctx.buffer(reserve=16 * 4)
        self.vao = self.ctx.vertex_array(self.program, [(self.vbo, "2f 2f", "in_pos", "in_uv")])

    @property
    def window_size(self):
        surface = pygame.display.get_surface()
        if surface:
            self.width, self.height = surface.get_size()
        return self.width, self.height

    def resize(self, size):
        self.width, self.height = size
        self.ctx.viewport = (0, 0, max(1, self.width), max(1, self.height))

    def present(self, surface, scale, offset_x, offset_y, shake_x=0, shake_y=0, enable_glow=False):
        win_w, win_h = self.window_size
        self.ctx.viewport = (0, 0, max(1, win_w), max(1, win_h))
        self.ctx.clear(0.047, 0.055, 0.047, 1.0)

        if self.texture.size != surface.get_size():
            self.texture.release()
            self.texture = self.ctx.texture(surface.get_size(), 4)
            self.texture.filter = (self.moderngl.LINEAR, self.moderngl.LINEAR)
            self.texture.repeat_x = False
            self.texture.repeat_y = False

        self.texture.write(pygame.image.tostring(surface, "RGBA", True))

        draw_w = max(1, int(surface.get_width() * scale))
        draw_h = max(1, int(surface.get_height() * scale))
        x = offset_x + shake_x
        y = offset_y + shake_y
        left = (x / win_w) * 2 - 1
        right = ((x + draw_w) / win_w) * 2 - 1
        top = 1 - (y / win_h) * 2
        bottom = 1 - ((y + draw_h) / win_h) * 2

        vertices = (
            left, bottom, 0.0, 0.0,
            right, bottom, 1.0, 0.0,
            left, top, 0.0, 1.0,
            right, top, 1.0, 1.0,
        )
        self.vbo.write(struct.pack("16f", *vertices))
        self.program["glow_enabled"].value = 1.0 if enable_glow else 0.0
        self.texture.use(0)
        self.vao.render(self.moderngl.TRIANGLE_STRIP)
        pygame.display.flip()

    def close(self):
        for resource in (getattr(self, "vao", None), getattr(self, "vbo", None), getattr(self, "texture", None), getattr(self, "program", None)):
            if resource is not None:
                resource.release()


def make_renderer(options, size, caption, opengl_cls=OpenGLRenderer):
    if options.renderer == "opengl":
        try:
            return opengl_cls(size, caption)
        except Exception as exc:
            print(f"Warning: OpenGL renderer unavailable ({exc}). Falling back to Pygame renderer.")
    return PygameRenderer(size, caption)
