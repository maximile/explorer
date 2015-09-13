#!/usr/bin/env python

import pyglet
import game.view
import game.game


def main():
    main_game = game.game.Game()
    window = game.view.GameWindow(main_game)
    pyglet.clock.schedule_interval(main_game.update, 1.0 / 60.0)
    pyglet.app.run()

if __name__ == '__main__':
    main()
