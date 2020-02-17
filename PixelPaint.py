"""
PixelPaint 1.1.0
"""


import main_win_process
import multiprocessing


if __name__ == "__main__":
    multiprocessing.freeze_support()

    main_win_process.run()
