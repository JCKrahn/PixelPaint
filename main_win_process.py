# -*- coding: utf-8 -*-

import paint_win_process
import ini_manager
import language
import os
import sys
import multiprocessing
import win32gui
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import cv2
import webbrowser
import pathlib2


def run():
    PixelPaint = QApplication(sys.argv)
    main_win = MainWindow()
    main_win.show()
    sys.exit(PixelPaint.exec_())


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__(None, Qt.WindowTitleHint | Qt.WindowCloseButtonHint)

        self.mainQ = multiprocessing.Queue()
        self.paintQ = multiprocessing.Queue()

        self.AppData = os.getenv('APPDATA') + "/PixelPaint"

        if os.path.isdir(self.AppData):

            if os.path.exists(self.AppData + "/PixelPaint.ini"):

                self.ini = ini_manager.get(self.AppData + "/PixelPaint.ini")
                # check ini; repair if necessary
                if "lang" not in self.ini:
                    self.ini["lang"] = "eng"
                if "win_xpos" not in self.ini:
                    self.ini["win_xpos"] = "75"
                if "win_ypos" not in self.ini:
                    self.ini["win_ypos"] = "75"
                if "image_maxsize" not in self.ini:
                    self.ini["image_maxsize"] = "true"
                if "fill_alg_only_connected_pixels" not in self.ini:
                    self.ini["fill_alg_only_connected_pixels"] = "false"
                if "fill_alg_visual" not in self.ini:
                    self.ini["fill_alg_visual"] = "false"
                if "enable_fill_alg_tolerance" not in self.ini:
                    self.ini["enable_fill_alg_tolerance"] = "false"
                if "fill_alg_tolerance" not in self.ini:
                    self.ini["fill_alg_tolerance"] = "20"
                if "open_help_on_start" not in self.ini:
                    self.ini["open_help_on_start"] = "false"

            else:
                self.ini = {
                    "lang": "eng",
                    "win_xpos": "75",
                    "win_ypos": "75",
                    "image_maxsize": "true",
                    "fill_alg_only_connected_pixels": "false",
                    "fill_alg_visual": "false",
                    "enable_fill_alg_tolerance": "false",
                    "fill_alg_tolerance": "20",
                    "open_help_on_start": "true"
                }

        else:
            pathlib2.Path(self.AppData).mkdir(exist_ok=True)
            self.ini = {
                "lang": "eng",
                "win_xpos": "75",
                "win_ypos": "75",
                "image_maxsize": "true",
                "fill_alg_only_connected_pixels": "false",
                "fill_alg_visual": "false",
                "enable_fill_alg_tolerance": "false",
                "fill_alg_tolerance": "20",
                "open_help_on_start": "true"
            }

        if self.ini["lang"] == "eng": self.lang = language.eng
        elif self.ini["lang"] == "ger": self.lang = language.ger

        self.paint_win_open = False
        self.image_info = [None,None,None,1,False]  # [filepath, filetype, compression/ quality, size-multi, greyscale]
        self.save_request = False
        self.draw_thickness = "1*1"
        self.colors = []  # list of colors from color palette

        self.move(int(self.ini["win_xpos"]), int(self.ini["win_ypos"]))
        self.setFixedWidth(846)
        self.setFixedHeight(61)
        self.setWindowTitle("PixelPaint")
        self.setWindowIcon(QIcon("data/icons/icon.png"))

        # Menu Bar
        menu = self.menuBar()

        #   File Menu
        File = menu.addMenu(self.lang["file"])

        file_create_new = QAction(self.lang["new"], self)
        file_create_new.setShortcut("N")
        file_create_new.triggered.connect(self.create_new)
        File.addAction(file_create_new)

        file_open = QAction(self.lang["open"], self)
        file_open.triggered.connect(self.open)
        file_open.setShortcut("O")
        File.addAction(file_open)

        file_save = QAction(self.lang["quick save"], self)
        file_save.triggered.connect(self.quick_save)
        file_save.setShortcut("S")
        File.addAction(file_save)

        file_save_as = QAction(self.lang["save"], self)
        file_save_as.triggered.connect(self.save)
        File.addAction(file_save_as)

        file_exit = QAction(self.lang["exit"], self)
        file_exit.triggered.connect(self.close)
        File.addAction(file_exit)

        #   Settings Menu
        settings = menu.addMenu(self.lang["settings"])

        settings_general = QAction(self.lang["general settings"], self)
        settings_general.triggered.connect(self.open_general_settings_menu)
        settings.addAction(settings_general)

        settings_paint_window = QAction(self.lang["paintwindow settings"], self)
        settings_paint_window.triggered.connect(self.open_paint_win_settings_menu)
        settings.addAction(settings_paint_window)

        #   Help Menu
        help_menu = menu.addMenu(self.lang["help"])

        help_action = QAction(self.lang["get help"], self)
        help_action.triggered.connect(self.open_help_page)
        help_menu.addAction(help_action)

        # Tool Bar
        tools = self.addToolBar(self.lang["tools"])
        tools.setToolTip(self.lang["tools"])
        tools.setMovable(False)

        self.draw_tool = Tool(self.lang["draw"], "data/icons/pencil.png")

        self.transparency_draw_tool = Tool(self.lang["draw transparency"],
            "data/icons/transparency_pencil.png")

        self.fill_tool = Tool(self.lang["fill"], "data/icons/paint_bucket.png")

        self.transparency_fill_tool = Tool(self.lang["fill transparency"],
            "data/icons/transparency_paint_bucket.png")

        self.erase_tool = Tool(self.lang["erase"], "data/icons/eraser.png")

        self.set_draw_width_button = SetDrawThicknessButton(self, self.lang["draw thickness"],
            "data/icons/width.png")

        self.undo_button = UnDoButton(self, self.lang["undo"], "data/icons/undo.png", self.paintQ)

        self.redo_button = ReDoButton(self, self.lang["redo"], "data/icons/redo.png", self.paintQ)

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
        color_palette = self.addToolBar(self.lang["color palette"])
        color_palette.setStyleSheet("spacing: 2px")
        color_palette.setToolTip(self.lang["color palette"])
        color_palette.setFixedHeight(40)
        color_palette.setMovable(False)
        color_palette.addSeparator()

        self.colors.append(Color(self.lang["color1/ main color"], (0, 0, 0)))
        color_palette.addWidget(self.colors[0])
        self.colors[0].setChecked(True)
        color_palette.addSeparator()

        for i in range(1, 16):
            self.colors.append(Color(self.lang["color"+str(i)], (255, 255, 255)))
            color_palette.addWidget(self.colors[i])

        # ----------------------------

        if self.ini["open_help_on_start"] == "true":
            self.ini["open_help_on_start"] = "false"
            self.open_help_page()

        self.process_comm_timer = QTimer()
        self.process_comm_timer.timeout.connect(self.process_comm)
        self.process_comm_timer.start(250)

    def process_comm(self):  # main_win_process  <->  paint_win_process
        if self.paint_win_open:

            # -> paintQ
            #   color
            for i in range(0, len(self.colors)):
                if self.colors[i].isChecked():
                    self.paintQ.put(["color", self.colors[i].color])

            #   tool
            if self.draw_tool.isChecked():
                self.paintQ.put(["tool", "draw"])
            elif self.transparency_draw_tool.isChecked():
                self.paintQ.put(["tool", "draw_transparency"])
            elif self.fill_tool.isChecked():
                self.paintQ.put(["tool", "fill"])
            elif self.transparency_fill_tool.isChecked():
                self.paintQ.put(["tool", "fill_transparency"])
            elif self.erase_tool.isChecked():
                self.paintQ.put(["tool", "erase"])
            else:
                self.paintQ.put(["tool", None])

            #   save request
            if self.save_request:
                self.paintQ.put(["request", ["save", self.image_info]])
                self.save_request = False

            #   draw_width
            self.paintQ.put(["draw_thickness", self.draw_thickness])

            #   fill_alg_only_connected_pixels
            self.paintQ.put(["fill_alg_only_connected_pixels", self.ini["fill_alg_only_connected_pixels"]])

            #   fill_alg_visual
            self.paintQ.put(["fill_alg_visual", self.ini["fill_alg_visual"]])

            #   fill_alg_tolerance
            self.paintQ.put(["fill_alg_tolerance", [self.ini["enable_fill_alg_tolerance"],
                self.ini["fill_alg_tolerance"]]])

            # mainQ <-
            while not self.mainQ.empty():
                gui_input = self.mainQ.get()

            #     paint window closed
                if gui_input == "paint_win_closed":
                    while not self.paintQ.empty():  # clear paintQ
                        try:
                            _ = self.paintQ.get()
                        except:
                            pass
                    while not self.mainQ.empty():  # clear mainQ
                        try:
                            _ = self.mainQ.get()
                        except:
                            pass
                    self.paint_win_open = False
                    self.image_info = [None,None,None,1,False]

            #     save
                elif gui_input == "save":
                    self.quick_save()

            #     close warning
                elif gui_input == "paint_win_close_request":
                    close_warning = CloseWarning(self, self.lang["close image"], self.lang["close warning"],
                        self.lang["close"], self.lang["cancel"])
                    if close_warning.exec_() == 1:
                        self.paintQ.put(["request", "close"])

                    close_warning.destroy()

            #     image to load is too big
                elif gui_input == "image_too_big":
                    error_message = ErrorMessage(self, "ERROR", self.lang["image too big text"])
                    error_message.show()

            #     permission error
                elif gui_input == "image_save_error":
                    error_message = ErrorMessage(self, "ERROR", self.lang["image save error"])
                    error_message.show()

            #     image load error
                elif gui_input == "image_load_error":
                    error_message = ErrorMessage(self, "ERROR", self.lang["image load error text"])
                    error_message.show()

            #     image format not supported
                elif gui_input == "image_format_not_supported":
                    error_message = ErrorMessage(self, "ERROR", self.lang["image format error text"])
                    error_message.show()

        self.process_comm_timer.start(250)

    def create_new(self):
        if not self.paint_win_open:
            prompt = NewPrompt(self, self.lang)
            if prompt.exec_() == 1:
                self.paint_win_open = True
                multiprocessing.Process(target=paint_win_process.run, args=(self.lang["untitled"], (prompt.config_width,
                    prompt.config_height), prompt.config_background, self.paintQ, self.mainQ, "true")).start()

            prompt.destroy()

    def open(self):
        if not self.paint_win_open:
            returned_path = list(QFileDialog.getOpenFileName(self, self.lang["open image"], "C:\\", "*.png *.jpg"))[0]
            try:
                returned_path.decode("ascii")  # check if ASCII

                self.image_info[0], self.image_info[1] = returned_path, returned_path[-3:]

                if os.path.exists(returned_path):

                    self.paint_win_open = True

                    img = cv2.imread(self.image_info[0], cv2.IMREAD_UNCHANGED)
                    multiprocessing.Process(target=paint_win_process.run, args=(self.image_info[0], (img.shape[1],
                        img.shape[0]), "Transparency", self.paintQ, self.mainQ, self.ini["image_maxsize"])).start()

            except UnicodeEncodeError:  # not ASCII
                error_message = ErrorMessage(self, "ERROR", self.lang["non ascii error"])
                error_message.show()

    def quick_save(self):
        if self.paint_win_open:
            if (self.image_info[0] is None) or (self.image_info[1] is None) or (self.image_info[2] is None):
                prompt = SavePrompt(self, self.lang)
                if prompt.exec_() == 1:
                    self.image_info = prompt.image_info

                    prompt.destroy()

                else:
                    prompt.destroy()
                    return 0

            self.save_request = True

    def save(self):
        if self.paint_win_open:
            prompt = SavePrompt(self, self.lang)
            if prompt.exec_() == 1:
                self.image_info = prompt.image_info

                prompt.destroy()

            else:
                prompt.destroy()
                return 0

            self.save_request = True

    def open_general_settings_menu(self):
        general_settings_menu = GeneralSettingsMenu(self, self.ini, self.lang)
        if general_settings_menu.exec_() == 1:
            self.ini = general_settings_menu.ini
            message = Message(self, self.lang["settings title"], self.lang["need to restart"])
            message.show()
            ini_manager.write(self.AppData+"/PixelPaint.ini", self.ini)

        general_settings_menu.destroy()

    def open_paint_win_settings_menu(self):
        paint_win_settings_menu = PaintWindowSettingsMenu(self, self.ini, self.lang)
        if paint_win_settings_menu.exec_() == 1:
            self.ini = paint_win_settings_menu.ini
            ini_manager.write(self.AppData+"/PixelPaint.ini", self.ini)

        paint_win_settings_menu.destroy()

    def open_help_page(self):
        if self.ini["lang"] == "eng":
            webbrowser.open(os.path.abspath("data/help/help_eng.html"), 2)
        elif self.ini["lang"] == "ger":
            webbrowser.open(os.path.abspath("data/help/help_ger.html"), 2)

    def closeEvent(self, *args, **kwargs):
        gui_id = win32gui.FindWindow(None, "PixelPaint")
        self.ini["win_xpos"] = str(win32gui.GetWindowRect(gui_id)[0])
        self.ini["win_ypos"] = str(win32gui.GetWindowRect(gui_id)[1])

        ini_manager.write(self.AppData+"/PixelPaint.ini", self.ini)

        self.paintQ.put(["request", "close"])


class Tool(QToolButton):
    def __init__(self, name, icon_path):
        super(Tool, self).__init__()
        self.setToolTip(name)
        self.setIcon(QIcon(icon_path))
        self.setAutoExclusive(True)
        self.installEventFilter(self)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseButtonPress:
            if event.button() == Qt.LeftButton:
                if not self.isChecked():
                    self.setCheckable(True)
                    self.setChecked(True)
                else:
                    self.setCheckable(False)
                    self.setChecked(False)
        return QObject.event(obj, event)


class Color(QToolButton):
    def __init__(self, name, color):
        super(Color, self).__init__()
        self.name = name
        self.setToolTip(self.name)
        self.color = color
        self.setCheckable(True)
        self.setAutoExclusive(True)
        self.installEventFilter(self)
        self.update_style()

    def update_style(self):
        self.setStyleSheet("Color { background-color: rgb" + str(self.color) + """;
                                    border-style: inset;
                                    border-width: 3px;
                                    border-color: rgb(180,180,180); }
                            Color:hover {
                                    border-width: 4px;
                                    border-color: rgb(25,195,255); }
                            Color:checked {
                                    border-color: rgb(226,87,76); }""")

    def color_picker(self):
        if self.color != (0, 0, 0):  # (black doesnt work as initial color)
            self.color = QColorDialog.getColor(parent=self.parent().parent(), initial=QColor(*self.color)).getRgb()[:3]
        else:
            self.color = QColorDialog.getColor(parent=self.parent().parent()).getRgb()[:3]  # initial color = white
        self.update_style()

    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseButtonPress:
            if event.button() == Qt.LeftButton:
                self.setChecked(True)
            elif event.button() == Qt.RightButton:
                self.color_picker()
        return QObject.event(obj, event)


class SetDrawThicknessButton(QToolButton):
    def __init__(self, parent_win, name, icon_path):
        self.parent_win = parent_win
        super(SetDrawThicknessButton, self).__init__()
        self.setToolTip(name)
        self.setIcon(QIcon(icon_path))
        self.setPopupMode(self.InstantPopup)
        self.setMenu(SetDrawThicknessMenu(self))


class SetDrawThicknessMenu(QMenu):
    def __init__(self, parent):
        self.parent = parent
        super(SetDrawThicknessMenu, self).__init__()
        self.addAction(QIcon("data/icons/draw_thickness/1^2"), "1*1", self.change_draw_thickness)
        self.addAction(QIcon("data/icons/draw_thickness/3^2"), "3*3", self.change_draw_thickness)
        self.addAction(QIcon("data/icons/draw_thickness/5^2"), "5*5", self.change_draw_thickness)
        self.addAction(QIcon("data/icons/draw_thickness/7^2"), "7*7", self.change_draw_thickness)

    def change_draw_thickness(self):
        self.parent.parent_win.draw_thickness = self.sender().text()


class UnDoButton(QToolButton):
    def __init__(self, parent_win, name, icon_path, q):
        self.parent_win = parent_win
        self.q = q
        super(UnDoButton, self).__init__()
        self.setToolTip(name)
        self.setIcon(QIcon(icon_path))
        self.clicked.connect(self.undo)
        self.setShortcut("Z")
        self.triggered.connect(self.undo)

    def undo(self):
        if not self.q.full() and self.parent_win.paint_win_open:
            self.q.put(["request", "undo"])


class ReDoButton(QToolButton):
    def __init__(self, parent_win, name, icon_path, q):
        self.parent_win = parent_win
        self.q = q
        super(ReDoButton, self).__init__()
        self.setToolTip(name)
        self.setIcon(QIcon(icon_path))
        self.clicked.connect(self.redo)
        self.setShortcut("Y")
        self.triggered.connect(self.redo)

    def redo(self):
        if not self.q.full() and self.parent_win.paint_win_open:
            self.q.put(["request", "redo"])


class SavePrompt(QDialog):
    def __init__(self, parent, lang):
        super(SavePrompt, self).__init__(parent, Qt.WindowTitleHint | Qt.WindowCloseButtonHint)

        self.lang = lang
        self.filetype = None
        self.image_info = None  # [filepath, filetype, compression/ quality, size-multi, greyscale]

        self.setWindowTitle(lang["save image"])
        self.setMinimumWidth(240)
        self.setMaximumWidth(320)
        self.setMaximumHeight(300)
        self.setModal(True)

        main_layout = QVBoxLayout()

        # filepath
        file_path_layout = QHBoxLayout()
        self.file_path = QLineEdit()
        self.file_path.textChanged.connect(self.file_path_changed)
        search_file_path_button = QPushButton()
        search_file_path_button.setText(lang["save as"])
        search_file_path_button.clicked.connect(self.search_file_path)
        file_path_layout.addWidget(self.file_path)
        file_path_layout.addWidget(search_file_path_button)
        main_layout.addLayout(file_path_layout)

        # png compression
        self.png_compression_setting = QGroupBox()
        self.png_compression_setting.hide()
        self.png_compression_setting.setTitle(lang["png (set compression)"])
        png_compression_setting_layout = QVBoxLayout()
        self.png_compression_slider = QSlider(Qt.Horizontal)
        self.png_compression_slider.setMinimum(0)
        self.png_compression_slider.setMaximum(5)
        self.png_compression_slider.setValue(0)
        self.png_compression_slider.setTickPosition(QSlider.TicksBelow)
        self.png_compression_slider.setTickInterval(1)
        png_compression_setting_layout.addWidget(self.png_compression_slider)
        self.png_compression_setting.setLayout(png_compression_setting_layout)
        main_layout.addWidget(self.png_compression_setting)

        # jpg quality
        self.jpg_quality_setting = QGroupBox()
        self.jpg_quality_setting.hide()
        self.jpg_quality_setting.setTitle(lang["jpg (set quality)"])
        jpg_quality_setting_layout = QVBoxLayout()
        self.jpg_quality_slider = QSlider(Qt.Horizontal)
        self.jpg_quality_slider.setMinimum(1)
        self.jpg_quality_slider.setMaximum(100)
        self.jpg_quality_slider.setValue(100)
        self.jpg_quality_slider.setTickPosition(QSlider.TicksBelow)
        self.jpg_quality_slider.setTickInterval(10)
        jpg_quality_setting_layout.addWidget(self.jpg_quality_slider)
        self.jpg_quality_setting.setLayout(jpg_quality_setting_layout)
        main_layout.addWidget(self.jpg_quality_setting)

        # advanced settings
        advanced_settings = QGroupBox()
        advanced_settings.setTitle(lang["advanced settings"])
        advanced_settings_layout = QVBoxLayout()

        spacer_item = QSpacerItem(24, 6, QSizePolicy.Minimum)

        save_as_greyscale_img_layout = QHBoxLayout()
        save_as_greyscale_img_txt = QLabel()
        save_as_greyscale_img_txt.setText(lang["save as grayscale image"])
        save_as_greyscale_img_layout.addWidget(save_as_greyscale_img_txt)
        self.save_as_greyscale_img_button = QRadioButton()
        self.save_as_greyscale_img_button.setChecked(False)
        save_as_greyscale_img_layout.addItem(spacer_item)
        save_as_greyscale_img_layout.addWidget(self.save_as_greyscale_img_button)
        advanced_settings_layout.addLayout(save_as_greyscale_img_layout)

        advanced_settings_layout.addItem(spacer_item)

        save_enlarged_setting = QGroupBox()
        save_enlarged_setting.setTitle(lang["save enlarged"])
        save_enlarged_setting.setCheckable(True)
        save_enlarged_setting.setChecked(False)
        save_enlarged_setting_layout = QHBoxLayout()
        save_enlarged_text = QLabel()
        save_enlarged_text.setText(lang["size"])
        save_enlarged_setting_layout.addWidget(save_enlarged_text)
        self.set_size = QComboBox()
        self.set_size.addItem(lang["100% size"])
        self.set_size.addItem(lang["400% size"])
        self.set_size.addItem(lang["900% size"])
        self.set_size.addItem(lang["1600% size"])
        self.set_size.addItem(lang["2500% size"])
        self.set_size.addItem(lang["3600% size"])
        self.set_size.addItem(lang["4900% size"])
        self.set_size.addItem(lang["6400% size"])
        self.set_size.addItem(lang["8100% size"])
        self.set_size.addItem(lang["10000% size"])
        save_enlarged_setting_layout.addWidget(self.set_size)
        save_enlarged_setting.setLayout(save_enlarged_setting_layout)
        advanced_settings_layout.addWidget(save_enlarged_setting)

        advanced_settings.setLayout(advanced_settings_layout)
        main_layout.addWidget(advanced_settings)

        # buttons
        button_layout = QHBoxLayout()

        save_button = QPushButton()
        save_button.setText(lang["save"])
        save_button.clicked.connect(self.save_clicked)
        save_button.setDefault(True)
        button_layout.addWidget(save_button)

        cancel_button = QPushButton()
        cancel_button.setText(lang["cancel"])
        cancel_button.clicked.connect(lambda: self.done(0))
        button_layout.addWidget(cancel_button)

        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

    def file_path_changed(self):
        if self.file_path.text()[-4:] == ".png" or self.file_path.text()[-4:] == ".PNG":
            self.filetype = "png"
            self.jpg_quality_setting.hide()
            self.png_compression_setting.show()

        elif self.file_path.text()[-4:] == ".jpg" or self.file_path.text()[-4:] == ".JPG":
            self.filetype = "jpg"
            self.png_compression_setting.hide()
            self.jpg_quality_setting.show()

    def search_file_path(self):
        if self.file_path.text().find("\\") > 0:  # if  '/' in prev-path
            prev_path = self.file_path.text()[:len(self.file_path.text())-self.file_path.text()[::-1].find("/")]
        else:  # if '\' in prev-path
            prev_path = self.file_path.text()[:len(self.file_path.text()) - self.file_path.text()[::-1].find("\\")]

        if os.path.exists(prev_path):
            path, filetype = list(QFileDialog.getSaveFileName(self, self.lang["save image"], prev_path,"*.png;; *.jpg"))
        else:
            path, filetype = list(QFileDialog.getSaveFileName(self, self.lang["save image"], "C:\\", "*.png;; *.jpg"))

        try:
            path.decode("ascii")  # check if ASCII
        except UnicodeEncodeError:  # not ASCII
            path = None
            error_message = ErrorMessage(self, "ERROR", self.lang["non ascii error"])
            error_message.show()

        if path:
            # file extension
            if path[-4:] != ".png" and path[-4:] != ".jpg" \
            and path[-4:] != ".PNG" and path[-4:] != ".JPG":
                self.filetype = filetype[2:]  # (without ".")
                path = path + "." + self.filetype
            else:
                self.filetype = path[2:]  # (without ".")

            self.file_path.setText(path)

            if self.filetype == "JPG" or self.filetype == "jpg":
                self.png_compression_setting.hide()
                self.jpg_quality_setting.show()
            else:
                self.jpg_quality_setting.hide()
                self.png_compression_setting.show()

    def save_clicked(self):
        path = self.file_path.text()
        try:
            path.decode("ascii")  # check if ASCII

            # check if valid path
            if os.path.exists(path[:len(path)-path[::-1].find("/")]):
                # check if valid file extension
                if path[-4:] == ".png" or path[-4:] == ".jpg" or path[-4:] == ".PNG" or path[0][-4:] == ".JPG":

                    if self.png_compression_setting.isVisible():
                        self.image_info = [path, self.filetype, self.png_compression_slider.value(),
                            int(self.set_size.currentText()[:-1]) / 100, self.save_as_greyscale_img_button.isChecked()]
                        self.done(1)
                        return 0

                    elif self.jpg_quality_setting.isVisible():
                        self.image_info = [path, self.filetype, self.jpg_quality_slider.value(),
                            int(self.set_size.currentText()[:-1]) / 100, self.save_as_greyscale_img_button.isChecked()]
                        self.done(1)
                        return 0

            # not valid
            error_message = ErrorMessage(self, "ERROR", self.lang["cant save image to this path"])
            error_message.show()

        except UnicodeEncodeError:  # not ASCII
            error_message = ErrorMessage(self, "ERROR", self.lang["non ascii error"])
            error_message.show()

    # has to be destroyed externally when closing via done()

    def closeEvent(self, *args, **kwargs):
        self.destroy()


class NewPrompt(QDialog):
    def __init__(self, parent, lang):
        super(NewPrompt, self).__init__(parent)

        self.lang = lang
        self.config_width = "64"
        self.config_height = "64"
        self.config_background = (255, 255, 255, 0)

        self.setModal(True)
        self.setWindowTitle(self.lang["new"])
        self.setFixedSize(178, 130)
        self.setModal(True)
        self.setWhatsThis(self.lang["new project general desc"])

        main_layout = QVBoxLayout()
        set_width_layout = QHBoxLayout()
        set_height_layout = QHBoxLayout()
        set_background_layout = QHBoxLayout()

        setWidth_txt = QLabel()
        setWidth_txt.setText(self.lang["set width"])
        self.setWidth = QLineEdit()
        self.setWidth.setWhatsThis(self.lang["new project width desc"])
        self.setWidth.setValidator(QIntValidator())
        self.setWidth.setMaxLength(3)
        self.setWidth.textChanged.connect(self.update_width)

        setHeight_txt = QLabel()
        setHeight_txt.setText(self.lang["set height"])
        self.setHeight = QLineEdit()
        self.setHeight.setWhatsThis(self.lang["new project height desc"])
        self.setHeight.setValidator(QIntValidator())
        self.setHeight.setMaxLength(3)
        self.setHeight.textChanged.connect(self.update_height)

        setBackground_txt = QLabel()
        setBackground_txt.setText(self.lang["background"])
        self.setBackground = QComboBox()
        self.setBackground.addItem(self.lang["transparency"])
        self.setBackground.addItem(self.lang["color1"])
        self.setBackground.setWhatsThis(self.lang["new project background desc"])

        set_width_layout.addWidget(setWidth_txt)
        set_width_layout.addWidget(self.setWidth)
        main_layout.addLayout(set_width_layout)

        set_height_layout.addWidget(setHeight_txt)
        set_height_layout.addWidget(self.setHeight)
        main_layout.addLayout(set_height_layout)

        set_background_layout.addWidget(setBackground_txt)
        set_background_layout.addWidget(self.setBackground)
        main_layout.addLayout(set_background_layout)

        spacerItem = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        main_layout.addItem(spacerItem)

        buttonLayout = QHBoxLayout()

        open_button = QPushButton()
        open_button.setText(self.lang["open"])
        open_button.clicked.connect(self.open_clicked)
        buttonLayout.addWidget(open_button)

        cancel_button = QPushButton()
        cancel_button.setText(self.lang["cancel"])
        cancel_button.clicked.connect(lambda: self.done(0))
        buttonLayout.addWidget(cancel_button)

        main_layout.addLayout(buttonLayout)

        self.setLayout(main_layout)

    def update_width(self, txt):
        if len(txt) >= 1:
            self.config_width = txt
        else:
            self.config_width = ""

    def update_height(self, txt):
        if len(txt) >= 1:
            self.config_height = txt
        else:
            self.config_height = ""

    def open_clicked(self):
        if self.setBackground.currentText() == self.lang["transparency"]:
            self.config_background = (255, 255, 255, 0)
        elif self.setBackground.currentText() == self.lang["color1"]:
            self.config_background = self.parent().colors[0] + (255,)

        if self.config_width == "-" or self.config_width == "+": self.config_width = "1"
        if self.config_height == "-" or self.config_height == "+": self.config_height = "1"

        if len(self.config_width) >= 1 and len(self.config_height) >= 1:
            self.config_width = int(self.config_width)
            self.config_height = int(self.config_height)
            if self.config_width < 1: self.config_width = 1
            if self.config_height < 1: self.config_height = 1
            return self.done(1)

        if not len(self.config_width) >= 1:
            self.config_width = 64
            if not len(self.config_height) >= 1:
                self.config_height = 64
                return self.done(1)
            self.config_height = int(self.config_height)
            if self.config_height < 1: self.config_height = 1
            return self.done(1)

        if not len(self.config_height) >= 1:
            self.config_height = 64
            self.config_width = int(self.config_width)
            if self.config_width < 1: self.config_width = 1
            return self.done(1)

        self.config_width = int(self.config_width)
        self.config_height = int(self.config_height)
        if self.config_width < 1: self.config_width = 1
        if self.config_height < 1: self.config_height = 1
        return self.done(1)

    # has to be destroyed externally when closing via done()

    def closeEvent(self, *args, **kwargs):
        self.destroy()


class GeneralSettingsMenu(QDialog):
    def __init__(self, parent, ini, lang):
        super(GeneralSettingsMenu, self).__init__(parent, Qt.WindowTitleHint | Qt.WindowCloseButtonHint)

        self.ini = ini
        self.lang = lang

        self.setWindowTitle(lang["general settings"])
        self.setFixedSize(200, 110)
        self.setModal(True)

        mainLayout = QVBoxLayout()

        # Language Settings
        lang_group_box = QGroupBox()
        lang_group_box.setTitle(lang["language"])
        lang_group_box_layout = QVBoxLayout()
        self.lang_combo_box = QComboBox()
        if ini["lang"] == "eng":  # show active language
            self.lang_combo_box.addItem(lang["english"])
            self.lang_combo_box.addItem(lang["german"])
        if ini["lang"] == "ger":
            self.lang_combo_box.addItem(lang["german"])
            self.lang_combo_box.addItem(lang["english"])
        lang_group_box_layout.addWidget(self.lang_combo_box)
        lang_group_box.setLayout(lang_group_box_layout)
        mainLayout.addWidget(lang_group_box)

        # Ok/ Cancel Button
        button_box = QHBoxLayout()
        ok_button = QPushButton()
        ok_button.setText("Ok")
        ok_button.clicked.connect(self.ok_clicked)
        button_box.addWidget(ok_button)
        cancel_button = QPushButton()
        cancel_button.setText(lang["cancel"])
        cancel_button.clicked.connect(lambda: self.done(0))
        button_box.addWidget(cancel_button)
        mainLayout.addLayout(button_box)

        self.setLayout(mainLayout)

    def ok_clicked(self):
        if self.lang_combo_box.currentText() == self.lang["english"]: self.ini["lang"] = "eng"
        else: self.ini["lang"] = "ger"

        self.done(1)

    # has to be destroyed externally when closing via done()

    def closeEvent(self, *args, **kwargs):
        self.destroy()


class PaintWindowSettingsMenu(QDialog):
    def __init__(self, parent, ini, lang):
        super(PaintWindowSettingsMenu, self).__init__(parent, Qt.WindowTitleHint | Qt.WindowCloseButtonHint)

        self.ini = ini
        self.lang = lang

        self.setWindowTitle(lang["paintwindow settings"])
        self.setFixedSize(275, 246)
        self.setModal(True)

        mainLayout = QVBoxLayout()

        spacer_item_1 = QSpacerItem(40, 6, QSizePolicy.Minimum)
        spacer_item_2 = QSpacerItem(30, 6, QSizePolicy.Minimum)
        spacer_item_3 = QSpacerItem(25, 6, QSizePolicy.Minimum)

        # Fill Tool Settings
        fill_tool_settings_group = QGroupBox()
        fill_tool_settings_group.setTitle(lang["fill tool settings"])
        fill_tool_settings_layout = QVBoxLayout()

        fill_alg_only_connected_pixels_layout = QHBoxLayout()
        fill_alg_only_connected_pixels_txt = QLabel()
        fill_alg_only_connected_pixels_txt.setText(lang["fill only connected pixels"])
        fill_alg_only_connected_pixels_layout.addWidget(fill_alg_only_connected_pixels_txt)
        self.fill_alg_only_connected_pixels_button = QRadioButton()
        self.fill_alg_only_connected_pixels_button.setAutoExclusive(False)
        if ini["fill_alg_only_connected_pixels"] == "true": self.fill_alg_only_connected_pixels_button.setChecked(True)
        fill_alg_only_connected_pixels_layout.addItem(spacer_item_2)
        fill_alg_only_connected_pixels_layout.addWidget(self.fill_alg_only_connected_pixels_button)
        fill_tool_settings_layout.addLayout(fill_alg_only_connected_pixels_layout)

        fill_tool_settings_layout.addItem(spacer_item_1)

        fill_alg_visual_button_layout = QHBoxLayout()
        fill_alg_visual_button_txt = QLabel()
        fill_alg_visual_button_txt.setText(lang["visualize fill algorithm"])
        fill_alg_visual_button_layout.addWidget(fill_alg_visual_button_txt)
        self.fill_alg_visual_button = QRadioButton()
        self.fill_alg_visual_button.setAutoExclusive(False)
        if ini["fill_alg_visual"] == "true": self.fill_alg_visual_button.setChecked(True)
        fill_alg_visual_button_layout.addItem(spacer_item_3)
        fill_alg_visual_button_layout.addWidget(self.fill_alg_visual_button)
        fill_tool_settings_layout.addLayout(fill_alg_visual_button_layout)

        fill_tool_settings_layout.addItem(spacer_item_1)

        self.fill_tool_tolerance_group = QGroupBox()
        self.fill_tool_tolerance_group.setTitle(lang["fill tool tolerance"])
        self.fill_tool_tolerance_group.setCheckable(True)
        if ini["enable_fill_alg_tolerance"] == "true": self.fill_tool_tolerance_group.setChecked(True)
        else: self.fill_tool_tolerance_group.setChecked(False)
        set_fill_tool_tolerance_layout = QHBoxLayout()
        set_fill_tool_tolerance_txt = QLabel()
        set_fill_tool_tolerance_txt.setText(lang["tolerance"])
        set_fill_tool_tolerance_layout.addWidget(set_fill_tool_tolerance_txt)
        self.set_fill_tool_tolerance = QSpinBox()
        self.set_fill_tool_tolerance.setMinimum(1)
        self.set_fill_tool_tolerance.setValue(int(ini["fill_alg_tolerance"]))
        set_fill_tool_tolerance_layout.addWidget(self.set_fill_tool_tolerance)
        self.fill_tool_tolerance_group.setLayout(set_fill_tool_tolerance_layout)
        fill_tool_settings_layout.addWidget(self.fill_tool_tolerance_group)

        fill_tool_settings_group.setLayout(fill_tool_settings_layout)

        mainLayout.addWidget(fill_tool_settings_group)

        # ImageLoad Settings
        image_load_settings_group = QGroupBox()
        image_load_settings_group.setTitle(lang["imageload settings"])
        image_load_settings_layout = QVBoxLayout()

        image_maxsize_layout = QHBoxLayout()
        image_maxsize_txt = QLabel()
        image_maxsize_txt.setText(lang["enable maxsize"])
        image_maxsize_layout.addWidget(image_maxsize_txt)
        self.image_maxsize_button = QRadioButton()
        if ini["image_maxsize"] == "true": self.image_maxsize_button.setChecked(True)
        def image_loader_maxsize_button_clicked():
            if not self.image_maxsize_button.isChecked():
                message = Message(self, self.lang["paintwindow settings"],
                    self.lang["image maxsize warning"])
                message.show()
        self.image_maxsize_button.clicked.connect(image_loader_maxsize_button_clicked)
        image_maxsize_layout.addWidget(self.image_maxsize_button)
        image_load_settings_layout.addLayout(image_maxsize_layout)

        image_load_settings_group.setLayout(image_load_settings_layout)

        mainLayout.addWidget(image_load_settings_group)

        # Ok/ Cancel Button
        button_box = QHBoxLayout()
        ok_button = QPushButton()
        ok_button.setText("Ok")
        ok_button.clicked.connect(self.ok_clicked)
        button_box.addWidget(ok_button)
        cancel_button = QPushButton()
        cancel_button.setText(lang["cancel"])
        cancel_button.clicked.connect(lambda: self.done(0))
        button_box.addWidget(cancel_button)
        mainLayout.addLayout(button_box)

        self.setLayout(mainLayout)

    def ok_clicked(self):
        if self.fill_alg_only_connected_pixels_button.isChecked(): self.ini["fill_alg_only_connected_pixels"] = "true"
        else: self.ini["fill_alg_only_connected_pixels"] = "false"

        if self.fill_alg_visual_button.isChecked(): self.ini["fill_alg_visual"] = "true"
        else: self.ini["fill_alg_visual"] = "false"

        if self.fill_tool_tolerance_group.isChecked(): self.ini["enable_fill_alg_tolerance"] = "true"
        else: self.ini["enable_fill_alg_tolerance"] = "false"

        self.ini["fill_alg_tolerance"] = self.set_fill_tool_tolerance.text()

        if self.image_maxsize_button.isChecked(): self.ini["image_maxsize"] = "true"
        else: self.ini["image_maxsize"] = "false"

        self.done(1)

    # has to be destroyed externally when closing via done()

    def closeEvent(self, *args, **kwargs):
        self.destroy()


class Message(QDialog):
    def __init__(self, parent, title, text):
        super(Message, self).__init__(parent, Qt.WindowTitleHint | Qt.WindowCloseButtonHint)

        self.setWindowTitle(title)
        self.setWindowIcon(QIcon("data/icons/icon.png"))
        self.setModal(True)

        main_layout = QVBoxLayout()

        text_label = QLabel()
        lines = text.count("\n") + 1
        text_label.setMinimumHeight(lines * 20)
        text_label.setText(text)
        text_label.setStyleSheet("background-color: rgb(220,220,220);")
        main_layout.addWidget(text_label)

        button_layout = QHBoxLayout()
        ok_button = QPushButton()
        ok_button.setText("Ok")
        ok_button.clicked.connect(self.close)
        button_layout.addWidget(ok_button)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

    def closeEvent(self, *args, **kwargs):
        self.destroy()


class CloseWarning(QDialog):
    def __init__(self, parent, title, text, close_button_text, cancel_button_text):
        super(CloseWarning, self).__init__(parent, Qt.WindowTitleHint | Qt.WindowCloseButtonHint)

        self.setWindowTitle(title)
        self.setWindowIcon(QIcon("data/icons/icon.png"))
        self.setModal(True)

        main_layout = QVBoxLayout()

        text_label = QLabel()
        lines = text.count("\n") + 1
        text_label.setMinimumHeight(lines * 20)
        text_label.setText(text)
        text_label.setStyleSheet("background-color: rgb(220,220,220);")
        main_layout.addWidget(text_label)

        button_layout = QHBoxLayout()
        close_button = QPushButton()
        close_button.setText(close_button_text)
        close_button.clicked.connect(lambda: self.done(1))
        cancel_button = QPushButton()
        cancel_button.setText(cancel_button_text)
        cancel_button.clicked.connect(lambda: self.done(0))
        button_layout.addWidget(close_button)
        button_layout.addWidget(cancel_button)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

    # has to be destroyed externally when closing via done()

    def closeEvent(self, *args, **kwargs):
        self.destroy()


class ErrorMessage(QDialog):
    def __init__(self, parent, title, text):
        super(ErrorMessage, self).__init__(parent, Qt.WindowTitleHint | Qt.WindowCloseButtonHint)

        self.setWindowTitle(title)
        self.setWindowIcon(QIcon("data/icons/error.png"))
        self.setModal(True)

        main_layout = QVBoxLayout()

        text_label = QLabel()
        lines = text.count("\n") + 1
        text_label.setMinimumHeight(lines * 20)
        text_label.setText(text)
        text_label.setStyleSheet("background-color: rgb(220,220,220);")
        main_layout.addWidget(text_label)

        button_layout = QHBoxLayout()
        ok_button = QPushButton()
        ok_button.setText("Ok")
        ok_button.clicked.connect(self.close)
        button_layout.addWidget(ok_button)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

    def closeEvent(self, *args, **kwargs):
        self.destroy()
