# The script of the game goes in this file.

# Declare characters used by this game. The color argument colorizes the
# name of the character.

# define e = Character("Eileen")


# The game starts here.

label start:
    pause
    show eileen happy
    pause
    show expression Holo("eileen happy") as eileen
    pause

    # This ends the game.

    return
