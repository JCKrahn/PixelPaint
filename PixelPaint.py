# -*- coding: utf-8 -*-
"""
PixelPaint 1.0
(GUI/ Main)
"""


import sys
import os
import numpy
import cv2
import win32gui
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import webbrowser
import multiprocessing
import paint_process
import gui_classes
import pathlib2
import ini_manager
import language


# GUI ------------------------------------------------------------------------------------------------------------------
class GUI(QMainWindow):
    def __init__(self, AppData, ini):
        super(GUI, self).__init__()
        # -----------------
        self.image_opened = False
        self.image_file = None  # (filename, file type)
        self.mainColor = None
        self.save_request = (False, None)  # (True/False, path)
        self.mainColor = None
        self.draw_width = "1*1"

        self.AppData = AppData
        self.ini = ini
        if self.ini["lang"] == "eng": self.lang = language.eng
        elif self.ini["lang"] == "ger": self.lang = language.ger
        # -----------------

        self.move(int(self.ini["win_xpos"]), int(self.ini["win_ypos"]))
        self.setFixedWidth(846)
        self.setFixedHeight(61)
        self.setWindowTitle("PixelPaint")
        self.setWindowIcon(QIcon("data/icons/icon.png"))

        # Menu Bar
        menu = self.menuBar()

        # --File Menu
        file_create_new = QAction(self.lang["new"], self)
        file_create_new.setShortcut("N")
        file_create_new.triggered.connect(self.create_new)
        file_open = QAction(self.lang["open"], self)
        file_open.triggered.connect(self.open)
        file_open.setShortcut("O")
        file_save = QAction(self.lang["save"], self)
        file_save.triggered.connect(self.save)
        file_save.setShortcut("S")
        file_save_as = QAction(self.lang["save as"], self)
        file_save_as.triggered.connect(self.save_as)
        file_exit = QAction(self.lang["exit"], self)
        file_exit.triggered.connect(self.close)
        File = menu.addMenu(self.lang["file"])
        File.addAction(file_create_new)
        File.addAction(file_open)
        File.addAction(file_save)
        File.addAction(file_save_as)
        File.addAction(file_exit)

        # --Settings Menu
        settings = menu.addMenu(self.lang["settings"])

        settings_general = QAction(self.lang["general settings"], self)
        settings_general.triggered.connect(self.open_general_settings_menu)
        settings.addAction(settings_general)

        settings_paint_window = QAction(self.lang["paintwindow settings"], self)
        settings_paint_window.triggered.connect(self.open_paint_window_settings_menu)
        settings.addAction(settings_paint_window)

        # --Help Menu
        help_menu = menu.addMenu(self.lang["help"])

        help_action = QAction(self.lang["get help"], self)
        help_action.triggered.connect(self.open_help_page)
        help_menu.addAction(help_action)

        # Tool Bar
        tools = self.addToolBar(self.lang["tools"])
        tools.setToolTip(self.lang["tools"])
        tools.setMovable(False)

        self.draw_tool = gui_classes.Tool(self.lang["draw"], "data/icons/pencil.png")

        self.transparency_draw_tool = gui_classes.Tool(self.lang["draw transparency"],
            "data/icons/transparency_pencil.png")

        self.fill_tool = gui_classes.Tool(self.lang["fill"], "data/icons/paint_bucket.png")

        self.transparency_fill_tool = gui_classes.Tool(self.lang["fill transparency"],
            "data/icons/transparency_paint_bucket.png")

        self.erase_tool = gui_classes.Tool(self.lang["erase"], "data/icons/eraser.png")

        self.set_draw_width_button = gui_classes.SetDrawWidthButton(self, self.lang["draw width"],
            "data/icons/width.png")

        self.undo_button = gui_classes.UnDoButton(self, self.lang["undo"], "data/icons/undo.png", paint_input_q)

        self.redo_button = gui_classes.ReDoButton(self, self.lang["redo"], "data/icons/redo.png", paint_input_q)

        tools.addWidget(self.draw_tool)
        tools.addWidget(self.transparency_draw_tool)
        tools.addWidget(self.fill_tool)
        tools.addWidget(self.transparency_fill_tool)
        tools.addWidget(self.erase_tool)
        tools.addSeparator()
        tools.addWidget(self.set_draw_width_button)
        tools.addSeparator()
        tools.addWidget(self.undo_button)
        tools.addWidget(self.redo_button)
        tools.addSeparator()

        # Color Palette
        # -- ColorTools
        self.color1 = gui_classes.Color(self.lang["color1/ main color"], (0, 0, 0))
        self.color2 = gui_classes.Color(self.lang["color2"], (255, 255, 255))
        self.color3 = gui_classes.Color(self.lang["color3"], (255, 255, 255))
        self.color4 = gui_classes.Color(self.lang["color4"], (255, 255, 255))
        self.color5 = gui_classes.Color(self.lang["color5"], (255, 255, 255))
        self.color6 = gui_classes.Color(self.lang["color6"], (255, 255, 255))
        self.color7 = gui_classes.Color(self.lang["color7"], (255, 255, 255))
        self.color8 = gui_classes.Color(self.lang["color8"], (255, 255, 255))
        self.color9 = gui_classes.Color(self.lang["color9"], (255, 255, 255))
        self.color10 = gui_classes.Color(self.lang["color10"], (255, 255, 255))
        self.color11 = gui_classes.Color(self.lang["color11"], (255, 255, 255))
        self.color12 = gui_classes.Color(self.lang["color12"], (255, 255, 255))
        self.color13 = gui_classes.Color(self.lang["color13"], (255, 255, 255))
        self.color14 = gui_classes.Color(self.lang["color14"], (255, 255, 255))
        self.color15 = gui_classes.Color(self.lang["color15"], (255, 255, 255))
        self.color16 = gui_classes.Color(self.lang["color16"], (255, 255, 255))

        color_palette = self.addToolBar(self.lang["color palette"])
        color_palette.setStyleSheet("spacing: 2px")
        color_palette.setToolTip(self.lang["color palette"])
        color_palette.setFixedHeight(40)
        color_palette.setMovable(False)
        color_palette.addSeparator()
        color_palette.addWidget(self.color1)
        self.color1.setChecked(True)
        self.mainColor = self.color1.color
        color_palette.addSeparator()
        color_palette.addWidget(self.color2)
        color_palette.addWidget(self.color3)
        color_palette.addWidget(self.color4)
        color_palette.addWidget(self.color5)
        color_palette.addWidget(self.color6)
        color_palette.addWidget(self.color7)
        color_palette.addWidget(self.color8)
        color_palette.addWidget(self.color9)
        color_palette.addWidget(self.color10)
        color_palette.addWidget(self.color11)
        color_palette.addWidget(self.color12)
        color_palette.addWidget(self.color13)
        color_palette.addWidget(self.color14)
        color_palette.addWidget(self.color15)
        color_palette.addWidget(self.color16)

        self.installEventFilter(self)

        # open help-page on first start
        if self.ini["open_help_on_start"] == "true":
            self.ini["open_help_on_start"] = "false"
            self.open_help_page()

        # event-handler timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.event_handler)
        self.timer.start(250)

    def event_handler(self):  # gui/ main -process (gui_input_q)  <->  paint-process (paint_input_q)
        if self.image_opened:
            # -> paint-process
            #     color
            if self.color1.isChecked():
                paint_input_q.put(["color", self.color1.color])
            elif self.color2.isChecked():
                paint_input_q.put(["color", self.color2.color])
            elif self.color3.isChecked():
                paint_input_q.put(["color", self.color3.color])
            elif self.color4.isChecked():
                paint_input_q.put(["color", self.color4.color])
            elif self.color5.isChecked():
                paint_input_q.put(["color", self.color5.color])
            elif self.color6.isChecked():
                paint_input_q.put(["color", self.color6.color])
            elif self.color7.isChecked():
                paint_input_q.put(["color", self.color7.color])
            elif self.color8.isChecked():
                paint_input_q.put(["color", self.color8.color])
            elif self.color9.isChecked():
                paint_input_q.put(["color", self.color9.color])
            elif self.color10.isChecked():
                paint_input_q.put(["color", self.color10.color])
            elif self.color11.isChecked():
                paint_input_q.put(["color", self.color11.color])
            elif self.color12.isChecked():
                paint_input_q.put(["color", self.color12.color])
            elif self.color13.isChecked():
                paint_input_q.put(["color", self.color13.color])
            elif self.color14.isChecked():
                paint_input_q.put(["color", self.color14.color])
            elif self.color15.isChecked():
                paint_input_q.put(["color", self.color15.color])
            elif self.color16.isChecked():
                paint_input_q.put(["color", self.color16.color])

            #     tool
            if self.draw_tool.isChecked():
                paint_input_q.put(["tool", "draw"])
            elif self.transparency_draw_tool.isChecked():
                paint_input_q.put(["tool", "draw_transparency"])
            elif self.fill_tool.isChecked():
                paint_input_q.put(["tool", "fill"])
            elif self.transparency_fill_tool.isChecked():
                paint_input_q.put(["tool", "fill_transparency"])
            elif self.erase_tool.isChecked():
                paint_input_q.put(["tool", "erase"])
            else:
                paint_input_q.put(["tool", None])

            #     draw width
            paint_input_q.put(["draw_width", self.draw_width])

            #     save request
            if self.save_request[0]:
                paint_input_q.put(["request", ["save", self.save_request[1]]])
                self.save_request = (False, None)

            #     visualize fill algorithm
            paint_input_q.put(["fill_alg_visual", self.ini["fill_alg_visual"]])

            #     fill tolerance
            paint_input_q.put(["fill_alg_tolerance", [self.ini["enable_fill_alg_tolerance"],
                self.ini["fill_alg_tolerance"]]])

            # main-process <-
            while not gui_input_q.empty():
                gui_input = gui_input_q.get()

            #     paint window closed
                if gui_input == "paint_win_closed":
                    while not paint_input_q.empty():  # clear paint process input queue
                        try:
                            _ = paint_input_q.get()
                        except:
                            pass
                    while not gui_input_q.empty():  # clear gui input queue
                        try:
                            _ = gui_input_q.get()
                        except:
                            pass
                    self.image_opened = False
                    self.image_file = None

            #     save
                elif gui_input == "save":
                    self.save()

            #     user wants to close paint win; ask for confirmation
                elif gui_input == "paint_win_close_request":
                    close_warning = gui_classes.CloseWarning(self, (152, 86), self.lang["close image"],
                        self.lang["close warning"], self.lang["close"], self.lang["cancel"])
                    if close_warning.exec_() == 1:
                        paint_input_q.put(["request", "close"])

            #     image to load is too big
                elif gui_input == "image_too_big":
                    error_message = gui_classes.ErrorMessage(self, (200, 84), "ERROR", self.lang["image too big text"])
                    error_message.show()

            #     image load error
                elif gui_input == "image_load_error":
                    error_message = gui_classes.ErrorMessage(self, (160, 84), "ERROR",
                        self.lang["image load error text"])
                    error_message.show()

            #     image format not supported
                elif gui_input == "image_format_not_supported":
                    error_message = gui_classes.ErrorMessage(self, (226, 72), "ERROR",
                        self.lang["image format error text"])
                    error_message.show()

            #     permission error
                elif gui_input == "permission_error":
                    error_message = gui_classes.ErrorMessage(self, (140, 72), "ERROR", "Permission Error")
                    error_message.show()

        self.timer.start(250)

    def create_new(self):  # opens ConfigurationPrompt -> create new project
        if not self.image_opened:
            prompt = gui_classes.NewProjectConfigPrompt(self, self.lang)
            if prompt.exec_() == 1:  # no error/ window not closed, user has configured his new project
                self.image_opened = True
                multiprocessing.Process(target=paint_process.paint_process,
                    args=(self.lang["untitled"], (prompt.config_width, prompt.config_height),  prompt.config_background,
                        paint_input_q, gui_input_q, "true")).start()

    def save(self):  # only ask for file name if file name is not known
        if self.image_opened:
            if not self.image_file:
                self.image_file = list(QFileDialog.getSaveFileName(self, self.lang["save image"], "C:\image",
                    "*.png;; *.jpg"))
            if self.image_file[0]:
                if self.image_file[0][-4:] != ".png" and self.image_file[0][-4:] != ".jpg" \
                        and self.image_file[0][-4:] != ".PNG" and self.image_file[0][-4:] != ".JPG":
                    self.image_file[0] = self.image_file[0] + self.image_file[1][1:]
                self.save_request = (True, self.image_file[0])

    def save_as(self):  # always ask for file name
        if self.image_opened:
            self.image_file = list(QFileDialog.getSaveFileName(self, self.lang["save image"], "C:\image",
                "*.png;; *.jpg"))
            if self.image_file[0]:
                if self.image_file[0][-4:] != ".png" and self.image_file[0][-4:] != ".jpg" \
                        and self.image_file[0][-4:] != ".PNG" and self.image_file[0][-4:] != ".JPG":
                    self.image_file[0] = self.image_file[0] + self.image_file[1][1:]
                self.save_request = (True, self.image_file[0])

    def open(self):
        if not self.image_opened:
            self.image_file = list(QFileDialog.getOpenFileName(self, self.lang["open image"], "C:\image",
                "*.png;; *.jpg"))
            if self.image_file[0]:
                if self.image_file[0][-4:] != ".png" and self.image_file[0][-4:] != ".jpg"\
                        and self.image_file[0][-4:] != ".PNG" and self.image_file[0][-4:] != ".JPG":
                    self.image_file[0] = self.image_file[0] + self.image_file[1][1:]
                self.image_opened = True
                img = cv2.imdecode(numpy.fromfile(self.image_file[0], numpy.uint8), cv2.IMREAD_UNCHANGED)
                multiprocessing.Process(target=paint_process.paint_process,
                    args=(self.image_file[0], (img.shape[1], img.shape[0]), "Transparency", paint_input_q, gui_input_q,
                        self.ini["image_maxsize"])).start()

    def open_general_settings_menu(self):
        general_settings_menu = gui_classes.GeneralSettingsMenu(self, self.ini, self.lang)
        if general_settings_menu.exec_() == 1:
            self.ini = general_settings_menu.ini
            message = gui_classes.Message(self, (212, 86), self.lang["settings title"], self.lang["need to restart"])
            message.show()
            ini_manager.write("data/PixelPaint.ini", self.ini)

    def open_paint_window_settings_menu(self):
        paint_window_settings_menu = gui_classes.PaintWindowSettings(self, self.ini, self.lang)
        if paint_window_settings_menu.exec_() == 1:
            self.ini = paint_window_settings_menu.ini
            ini_manager.write("data/PixelPaint.ini", self.ini)

    def open_help_page(self):
        if self.ini["lang"] == "eng":
            webbrowser.open(os.path.abspath("data/help/help_eng.html"), 2)
        elif self.ini["lang"] == "ger":
            webbrowser.open(os.path.abspath("data/help/help_ger.html"), 2)

    def closeEvent(self, *args, **kwargs):

        # save win position
        gui_id = win32gui.FindWindow(None, "PixelPaint")
        self.ini["win_xpos"] = str(win32gui.GetWindowRect(gui_id)[0])
        self.ini["win_ypos"] = str(win32gui.GetWindowRect(gui_id)[1])

        # write ini
        ini_manager.write(self.AppData+"/PixelPaint.ini", self.ini)

        # close paint window
        paint_input_q.put(["request", "close"])

# ----------------------------------------------------------------------------------------------------------------------


if __name__ == "__main__":
    multiprocessing.freeze_support()

    # AppData -------------------------------------------------------------------------
    AppData = os.getenv('APPDATA')+"/PixelPaint"

    if os.path.isdir(AppData):  # PixelPaint AppData exists

        if os.path.exists(AppData+"/PixelPaint.ini"):  # PixelPaint.ini exists

            ini = ini_manager.get(AppData+"/PixelPaint.ini")  # load ini

        else:  # PixelPaint.ini doesnt exist

            # create ini dict
            ini = {
                "lang": "eng",
                "win_xpos": "75",
                "win_ypos": "75",
                "image_maxsize": "true",
                "fill_alg_visual": "true",
                "enable_fill_alg_tolerance": "false",
                "fill_alg_tolerance": "2",
                "open_help_on_start": "true"
            }
            # ini will be saved when closing

    else:  # PixelPaint AppData doesnt exists

        pathlib2.Path(AppData).mkdir(exist_ok=True)  # create PixelPaint AppData

        # create ini dict
        ini = {
            "lang": "eng",
            "win_xpos": "75",
            "win_ypos": "75",
            "image_maxsize": "true",
            "fill_alg_visual": "true",
            "enable_fill_alg_tolerance": "false",
            "fill_alg_tolerance": "2",
            "open_help_on_start": "true"
        }
        # ini will be saved when closing
    # ---------------------------------------------------------------------------------

    paint_input_q = multiprocessing.Queue()
    gui_input_q = multiprocessing.Queue()

    app = QApplication(sys.argv)
    gui = GUI(AppData, ini)
    gui.show()

    sys.exit(app.exec_())
