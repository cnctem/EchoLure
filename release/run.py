# PyInstaller 打包入口脚本
# 用于解决打包后的资源路径问题

import sys
import os

# 确保在打包后能正确找到模块
if getattr(sys, 'frozen', False):
    # 运行在打包后的可执行文件中
    bundle_dir = sys._MEIPASS
else:
    # 运行在正常的 Python 环境中
    bundle_dir = os.path.dirname(os.path.abspath(__file__))

# 添加路径
sys.path.insert(0, bundle_dir)

from echolure.game import Game


def main():
    """游戏主入口"""
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
