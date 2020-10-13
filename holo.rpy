define holovalues = {'tintcolor' : '#06f', # la couleur dans laquelle sera teinte l'image
                     'totalpha' : .9, # la transparence "globale" de l'hologramme
                     'interalpha' : .75, # la transparence additionnelle appliquée une ligne sur deux
                     'blinking' : .5, # la fréquence à laquelle une frame sera rendue plus transparente que les autres (pour l'effet de clignotement)
                     'blinkalpha' : .9, # la transparence additionnelle appliquée pour l'effet de clignotement
                     'lineheight' : 4 # la hauteur des lignes affichées sur l'hologramme
                     }

init python:
    from pygame_sdl2 import Rect

    def blink(trans, st, at):
        if renpy.random.random() < holovalues['blinking']:
            trans.alpha = holovalues['blinkalpha']
        else:
            trans.alpha = 1
        return 0

    def Holo(child, tintcolor=holovalues['tintcolor'], totalpha=holovalues['totalpha'], interalpha=holovalues['interalpha'], lineheight=holovalues['lineheight']):
        child = renpy.easy.displayable(child)
        w, h = renpy.display.render.render(child, 0, 0, 0, 0).get_size()
        # only way I found to get the correct size !
        masq = HoloMask(w, h, totalpha, interalpha, lineheight)
        tinted = im.MatrixColor(child, im.matrix.desaturate()*im.matrix.tint(*Color(tintcolor).rgb)*im.matrix.brightness(.25))
        # tinted = im.MatrixColor(child, im.matrix.tint(*Color(tintcolor).rgb)*im.matrix.brightness(.2))
        return At(AlphaMask(tinted, masq), Transform(function=blink))

    class HoloMask(renpy.Displayable):
        """
        Custom Displayable
        used by Holo to get the alpha mask to apply to the child
        """
        def __init__(self, width, height, totalpha, interalpha, lineheight):
            super(HoloMask, self).__init__()
            self.width = width
            self.height = height
            self.totalpha = totalpha
            self.interalpha = interalpha
            self.lineheight = lineheight

        def render(self, width, height, st, at):
            rv = renpy.display.render.Render(self.width, self.height)
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
