define holovalues.tintcolor = '#06f' # la couleur dans laquelle sera teinte l'image
define holovalues.totalpha = .9 # la transparence "globale" de l'hologramme
define holovalues.interalpha = .75 # la transparence additionnelle appliquée une ligne sur deux
define holovalues.blinking = .5 # la fréquence à laquelle une frame sera rendue plus transparente que les autres (pour l'effet de clignotement)
define holovalues.blinkalpha = .9 # la transparence additionnelle appliquée pour l'effet de clignotement
define holovalues.lineheight = 4 # la hauteur des lignes affichées sur l'hologramme

init python:
    from functools import partial
    import random

    renpy.register_shader("gouvernathor.holostripes",
        variables="""
            uniform mat4 u_tintermatr;
            uniform float u_totalpha;
            uniform float u_interalpha;
            uniform float u_lineheight; // support absolute numbers of pixels

            attribute vec2 a_tex_coord;
            varying vec2 v_tex_coord;
            uniform float u_lod_bias;
            uniform sampler2D tex0;
        """, vertex_220="""
            v_tex_coord = a_tex_coord;
        """, fragment_220="""
            float thisalpha = u_totalpha;
            if (mod(v_tex_coord.y, 2*u_lineheight) > lineheight) {
                thisalpha = thisalpha * interalpha;
            }
            gl_FragColor = u_tintermatr * texture2D(tex0, v_tex_coord.st, u_lod_bias) * thisalpha;
        """)

    class holo(renpy.Displayable):
        def __init__(self, child,
                tintcolor=holovalues.tintcolor,
                totalpha=holovalues.totalpha,
                interalpha=holovalues.interalpha,
                blinking=holovalues.blinking,
                blinkalpha=holovalues.blinkalpha,
                lineheight=holovalues.lineheight,
                **properties):
            super().__init__(**properties)
            self.child = child
            self.tintcolor = tintcolor
            self.totalpha = totalpha
            self.interalpha = interalpha
            self.blinking = blinking
            self.blinkalpha = blinkalpha
            self.lineheight = lineheight

        def visit(self):
            return [self.child]

        def render(self, width, height, st, at):
            rv = renpy.render(self.child, width, height, st, at)

            rv.add_shader("gouvernathor.holostripes")
            rv.add_shader("-renpy.texture")

            tintcolor = self.tintmatrix
            if tintcolor:
                matrix = BrightnessMatrix(.25)*TintMatrix(Color(tintcolor))*SaturationMatrix(0)
            else:
                matrix = IdentityMatrix()
            rv.add_uniform("u_tintermatr", matrix)

            totalpha = self.totalpha
            interalpha = self.interalpha
            blinking = self.blinking
            if blinking != .0 and blinkalpha != 1.:
                renpy.redraw(self, 0)
                if random.random() < blinking:
                    blinkalpha = self.blinkalpha
                    totalpha *= blinkalpha
                    interalpha *= blinkalpha
            rv.add_uniform("u_totalpha", totalpha)
            rv.add_uniform("u_interalpha", interalpha)

            rv.add_uniform("u_lineheight", self.lineheight)

            return rv
