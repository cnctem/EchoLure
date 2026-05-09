"""回声定位炮 - 游戏入口

运行方式:
    uv run python main.py
"""

from echolure.game import Game


def main():
    """游戏主入口"""
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
