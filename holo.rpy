define holovalues = {'tintcolor' : '#06f', # la couleur dans laquelle sera teinte l'image
                     'totalpha' : .9, # la transparence "globale" de l'hologramme
                     'interalpha' : .75, # la transparence additionnelle appliquée une ligne sur deux
                     'blinking' : .5, # la fréquence à laquelle une frame sera rendue plus transparente que les autres (pour l'effet de clignotement)
                     'blinkalpha' : .9, # la transparence additionnelle appliquée pour l'effet de clignotement
                     'lineheight' : 4 # la hauteur des lignes affichées sur l'hologramme
                     }

init python:
    from pygame_sdl2 import Rect

    def blink(trans, st, at, blinking, blinkalpha):
        if renpy.random.random() < blinking:
            trans.alpha = blinkalpha
        else:
            trans.alpha = 1
        return 0

    class Holo(renpy.Displayable):
        """
        Custom Displayable
        Displays its child with a star wars-styled hologram effect,
        including tint, transparency, blinking and interlacing effects
        """
        def __init__(self, child,
                     tintcolor=holovalues['tintcolor'],
                     totalpha=holovalues['totalpha'],
                     interalpha=holovalues['interalpha'],
                     blinking=holovalues['blinking'],
                     blinkalpha=holovalues['blinkalpha'],
                     lineheight=holovalues['lineheight'],
                     **kwargs
                     ):
            super(Holo, self).__init__(**kwargs)
            self.child = renpy.displayable(child)
            self.tintcolor = tintcolor
            self.totalpha = totalpha
            self.interalpha = interalpha
            self.blinking = blinking
            self.blinkalpha = blinkalpha
            self.lineheight = lineheight
            self.alpha = totalpha

        def render(self, width, height, st, at):
            nwidth, nheight = renpy.render(self.child, width, height, st, at).get_size()
            masq = HoloMask(nwidth, nheight, self.alpha, self.interalpha, self.lineheight)
            if config.gl2:
                tinted = Transform(self.child, matrixcolor=BrightnessMatrix(.25)*TintMatrix(Color(self.tintcolor))*SaturationMatrix(0))
            else:
                tinted = im.MatrixColor(self.child, im.matrix.desaturate()*im.matrix.tint(*Color(self.tintcolor).rgb)*im.matrix.brightness(.25))
            t = Transform(AlphaMask(tinted, masq), function=renpy.curry(blink)(blinking=self.blinking, blinkalpha=self.blinkalpha))
            rv = renpy.Render(nwidth, nheight)
            rv.blit(renpy.render(t, nwidth, nheight, st, at), (0, 0))
            return rv

        def event(self, ev, x, y, st):
            return self.child.event(ev, x, y, st)

        def visit(self):
            return [self.child]

    class HoloMask(renpy.Displayable):
        """
        Custom Displayable
        used by Holo to get the alpha mask to apply to the child
        manages the interlacing effect ant the overall alpha
        """
        def __init__(self, width, height, totalpha, interalpha, lineheight):
            super(HoloMask, self).__init__()
            self.width = width
            self.height = height
            self.totalpha = totalpha
            self.interalpha = interalpha
            self.lineheight = lineheight

        def render(self, width, height, st, at):
            rv = renpy.Render(self.width, self.height)
            cv = rv.canvas()
            ytot = 0
            lcount = 0
            while ytot < self.height:
                # tracer un rectangle sur toute la largeur entre y=ytot et y=ytot+lineheight
                trp = self.totalpha * (self.interalpha if lcount%2 else 1)
                # trp = holovalues['totalpha'] * (lcount%2 ? holovalues['interalpha'] : 1)
                # transparence (lcount%2 ? totalpha*interalpha : totalpha)*255
                cv.rect(renpy.color.Color((255*trp,
                                           0,
                                           0,
                                           255*trp)),
                        Rect(0,
                             ytot,
                             self.width,
                             self.lineheight if (ytot+self.lineheight < self.height) else (self.height-ytot))
                        )
                ytot += self.lineheight
                lcount += 1
            return rv
