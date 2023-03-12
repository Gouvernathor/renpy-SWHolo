define holovalues.tintcolor = '#06f' # la couleur dans laquelle sera teinte l'image
define holovalues.totalpha = .9 # la transparence "globale" de l'hologramme
define holovalues.interalpha = .75 # la transparence additionnelle appliquée une ligne sur deux
define holovalues.blinking = .5 # la fréquence à laquelle une frame sera rendue plus transparente que les autres (pour l'effet de clignotement)
define holovalues.blinkalpha = .9 # la transparence additionnelle appliquée pour l'effet de clignotement
define holovalues.lineheight = 4 # la hauteur des lignes affichées sur l'hologramme

init python:
    from functools import partial
    from pygame_sdl2 import Rect

    def blink(trans, st, at, blinking, blinkalpha):
        if renpy.random.random() < blinking:
            trans.alpha = blinkalpha
        else:
            trans.alpha = 1
        return 0

    def holo(child,
             tintcolor=holovalues.tintcolor,
             totalpha=holovalues.totalpha,
             interalpha=holovalues.interalpha,
             blinking=holovalues.blinking,
             blinkalpha=holovalues.blinkalpha,
             lineheight=holovalues.lineheight,
             **kwargs):
        """
        A transform in the style of a renpy function
        Displays its child with a star wars-styled hologram effect,
        including tint, transparency, blinking and interlacing effects
        """
        if tintcolor:
            tinted = Transform(child, matrixcolor=BrightnessMatrix(.25)*TintMatrix(Color(tintcolor))*SaturationMatrix(0))
        else:
            tinted = child
        if lineheight and (interalpha != 1.0):
            hollo = Holo(tinted, totalpha, interalpha, lineheight, **kwargs)
        else:
            hollo = Transform(tinted, alpha=totalpha, **kwargs)
        if blinking != .0 and blinkalpha != 1.0:
            return Transform(hollo, function=partial(blink, blinking=blinking, blinkalpha=blinkalpha))
        else:
            return hollo

    class Holo(renpy.Displayable):
        """
        Custom Displayable
        manages the overall transparency and the interlacing effect
        """
        def __init__(self, child, totalpha, interalpha, lineheight, **kwargs):
            super(Holo, self).__init__(**kwargs)
            self.child = renpy.displayable(child)
            self.totalpha = totalpha
            self.interalpha = interalpha
            self.lineheight = lineheight

        def render(self, width, height, st, at):
            nwidth, nheight = renpy.render(self.child, width, height, st, at).get_size()
            masq = HoloMask(nwidth, nheight, self.totalpha, self.interalpha, self.lineheight)
            return renpy.render(AlphaMask(self.child, masq), width, height, st, at)

        def visit(self):
            return [self.child]

    class HoloMask(renpy.Displayable):
        """
        Custom Displayable
        used by Holo to get the alpha mask to apply to the child
        manages the interlacing effect and the overall alpha

        Works better visually than a Tile of a Vbox of two Solid.
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
                        (0,
                         ytot,
                         self.width,
                         self.lineheight if (ytot+self.lineheight < self.height) else (self.height-ytot)))
                ytot += self.lineheight
                lcount += 1
            return rv
