# -*- coding: utf-8 -*-
"""
GUI Classes
"""

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import os


# pop up windows -------------------------------------------------------------------------------------------------------
class GeneralSettingsMenu(QDialog):
    def __init__(self, parent, ini, lang):
        super(GeneralSettingsMenu, self).__init__(parent, Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        self.setWindowTitle(lang["general settings"])
        self.setFixedSize(200, 110)
        self.setModal(True)

        self.ini = ini
        self.lang = lang

        mainLayout = QVBoxLayout()

        # Language Settings --------------------------------------------------
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

        # Ok/ Cancel Button -------------------------------------------------
        button_box = QHBoxLayout()
        ok_button = QPushButton()
        ok_button.setText("Ok")
        ok_button.clicked.connect(self.ok)
        button_box.addWidget(ok_button)
        cancel_button = QPushButton()
        cancel_button.setText(lang["cancel"])
        cancel_button.clicked.connect(lambda: self.done(0))
        button_box.addWidget(cancel_button)
        mainLayout.addLayout(button_box)

        self.setLayout(mainLayout)

    def ok(self):
        if self.lang_combo_box.currentText() == self.lang["english"]: self.ini["lang"] = "eng"
        else: self.ini["lang"] = "ger"

        self.done(1)


class PaintWindowSettings(QDialog):
    def __init__(self, parent, ini, lang):
        super(PaintWindowSettings, self).__init__(parent, Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        self.setWindowTitle(lang["paintwindow settings"])
        self.setFixedSize(275, 246)
        self.setModal(True)

        self.ini = ini
        self.lang = lang

        mainLayout = QVBoxLayout()

        spacer_item_1 = QSpacerItem(40, 6, QSizePolicy.Minimum)
        spacer_item_2 = QSpacerItem(30, 6, QSizePolicy.Minimum)
        spacer_item_3 = QSpacerItem(25, 6, QSizePolicy.Minimum)

        # Fill Tool Settings ------------------------------------------------------
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

        # ImageLoader Settings ---------------------------------------------------
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

        # Ok/ Cancel Button -------------------------------------------------
        button_box = QHBoxLayout()
        ok_button = QPushButton()
        ok_button.setText("Ok")
        ok_button.clicked.connect(self.ok)
        button_box.addWidget(ok_button)
        cancel_button = QPushButton()
        cancel_button.setText(lang["cancel"])
        cancel_button.clicked.connect(lambda: self.done(0))
        button_box.addWidget(cancel_button)
        mainLayout.addLayout(button_box)

        self.setLayout(mainLayout)

    def ok(self):
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


class SavePrompt(QDialog):
    def __init__(self, parent, lang):
        super(SavePrompt, self).__init__(parent, Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        self.setWindowTitle(lang["save image"])
        self.setMinimumWidth(240)
        self.setMaximumWidth(320)
        self.setMaximumHeight(300)
        self.setModal(True)

        self.lang = lang

        self.filetype = None

        self.image_info = None  # [filepath, filetype, compression/ quality, size-multi, greyscale]

        main_layout = QVBoxLayout()

        # filepath
        file_path_layout = QHBoxLayout()
        self.file_path = QLineEdit()
        self.file_path.textChanged.connect(self.file_path_edit_text_changed)
        search_file_path_button = QPushButton()
        search_file_path_button.setText(lang["search"])
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
        save_button.clicked.connect(self.save)
        save_button.setDefault(True)
        button_layout.addWidget(save_button)

        cancel_button = QPushButton()
        cancel_button.setText(lang["cancel"])
        cancel_button.clicked.connect(lambda: self.done(0))
        button_layout.addWidget(cancel_button)

        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

    def file_path_edit_text_changed(self):
        if self.file_path.text()[-4:] == ".png" or self.file_path.text()[-4:] == ".PNG":
            self.filetype = "png"
            self.jpg_quality_setting.hide()
            self.png_compression_setting.show()

        elif self.file_path.text()[-4:] == ".jpg" or self.file_path.text()[-4:] == ".JPG":
            self.filetype = "jpg"
            self.png_compression_setting.hide()
            self.jpg_quality_setting.show()

    def search_file_path(self):
        img_file_path, filetype = list(QFileDialog.getSaveFileName(self, self.lang["save image"], "C:\image",
            "*.png;; *.jpg"))

        try:
            img_file_path.decode("ascii")  # check if ASCII
        except UnicodeEncodeError:  # image path not ASCII
            img_file_path = None
            error_message = ErrorMessage(self, "ERROR", self.lang["non ascii error"])
            error_message.show()

        if img_file_path:
            # file extension
            if img_file_path[-4:] != ".png" and img_file_path[-4:] != ".jpg" \
            and img_file_path[-4:] != ".PNG" and img_file_path[-4:] != ".JPG":
                self.filetype = filetype[2:]  # (without ".")
                img_file_path = img_file_path + "." + self.filetype
            else:
                self.filetype = img_file_path[2:]  # (without ".")

            self.file_path.setText(img_file_path)

            if self.filetype == "JPG" or self.filetype == "jpg":
                self.png_compression_setting.hide()
                self.jpg_quality_setting.show()
            else:
                self.jpg_quality_setting.hide()
                self.png_compression_setting.show()

    def save(self):
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

        except UnicodeEncodeError:  # image path not ASCII
            error_message = ErrorMessage(self, "ERROR", self.lang["non ascii error"])
            error_message.show()


class NewProjectConfigPrompt(QDialog):
    def __init__(self, parent, lang):
        self.lang = lang
        # standard values --
        self.config_width = "64"
        self.config_height = "64"
        self.config_background = (255, 255, 255, 0)
        # ------------------
        super(NewProjectConfigPrompt, self).__init__(parent)

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
        open_button.clicked.connect(self.return_config)
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

    def return_config(self):
        if self.setBackground.currentText() == self.lang["transparency"]:
            self.config_background = (255, 255, 255, 0)
        elif self.setBackground.currentText() == self.lang["color1"]:
            self.config_background = self.parent().mainColor + (255,)

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


class ErrorMessage(QDialog):
    def __init__(self, parent, title, text):
        super(ErrorMessage, self).__init__(parent, Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        self.setWindowTitle(title)
        self.setWindowIcon(QIcon("data/icons/error.png"))
        self.setModal(True)

        main_layout = QVBoxLayout()

        text_label = QLabel()
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


class Message(QDialog):
    def __init__(self, parent, title, text):
        super(Message, self).__init__(parent, Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        self.setWindowTitle(title)
        self.setWindowIcon(QIcon("data/icons/icon.png"))
        self.setModal(True)

        main_layout = QVBoxLayout()

        text_label = QLabel()
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


class CloseWarning(QDialog):
    def __init__(self, parent, title, text, close_button_text, cancel_button_text):
        super(CloseWarning, self).__init__(parent, Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        self.setWindowTitle(title)
        self.setWindowIcon(QIcon("data/icons/icon.png"))
        self.setModal(True)

        main_layout = QVBoxLayout()

        text_label = QLabel()
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

# ----------------------------------------------------------------------------------------------------------------------


# Buttons --------------------------------------------------------------------------------------------------------------
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
        if not self.q.full() and self.parent_win.image_opened:
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
        if not self.q.full() and self.parent_win.image_opened:
            self.q.put(["request", "redo"])
# ----------------------------------------------------------------------------------------------------------------------


# Tool -----------------------------------------------------------------------------------------------------------------
class Tool(QToolButton):
    def __init__(self, name, icon_path):
        super(Tool, self).__init__()
        self.setToolTip(name)
        self.setIcon(QIcon(icon_path))
        self.setAutoExclusive(True)
        self.installEventFilter(self)

    def eventFilter(self, obj, event):  # -> left_mouse_click: select/ unselect
        if event.type() == QEvent.MouseButtonPress:
            if event.button() == Qt.LeftButton:  # clicked:
                if not self.isChecked():  # not selected -> set selected
                    self.setCheckable(True)
                    self.setChecked(True)
                else:  # selected -> set unselected
                    self.setCheckable(False)
                    self.setChecked(False)
        return QObject.event(obj, event)
# ----------------------------------------------------------------------------------------------------------------------


#    SetDrawWidth Button  ----------------------------------------------------------------------------------------------
class SetDrawWidthMenu(QMenu):
    def __init__(self, parent):
        self.parent = parent
        super(SetDrawWidthMenu, self).__init__()
        self.addAction(QIcon("data/icons/draw_widths/1^2"), "1*1", self.change_draw_width)
        self.addAction(QIcon("data/icons/draw_widths/3^2"), "3*3", self.change_draw_width)
        self.addAction(QIcon("data/icons/draw_widths/5^2"), "5*5", self.change_draw_width)
        self.addAction(QIcon("data/icons/draw_widths/7^2"), "7*7", self.change_draw_width)

    def change_draw_width(self):
        self.parent.parent_win.draw_width = self.sender().text()


class SetDrawWidthButton(QToolButton):
    def __init__(self, parent_win, name, icon_path):
        self.parent_win = parent_win
        super(SetDrawWidthButton, self).__init__()
        self.setToolTip(name)
        self.setIcon(QIcon(icon_path))
        self.setPopupMode(self.InstantPopup)
        self.setMenu(SetDrawWidthMenu(self))
# ----------------------------------------------------------------------------------------------------------------------


# Color ----------------------------------------------------------------------------------------------------------------
class Color(QToolButton):  # ColorTool (select color | change via ColorDialog)
    def __init__(self, name, color):
        super(Color, self).__init__()
        self.name = name
        self.setToolTip(self.name)
        self.color = color
        self.setCheckable(True)
        self.setAutoExclusive(True)
        self.installEventFilter(self)
        self.update_style()

    def update_style(self):  # set StyleSheet
        self.setStyleSheet("Color { background-color: rgb" + str(self.color) + """;
                                    border-style: inset;
                                    border-width: 3px;
                                    border-color: rgb(180,180,180); }
                            Color:hover {
                                    border-width: 4px;
                                    border-color: rgb(25,195,255); }
                            Color:checked {
                                    border-color: rgb(226,87,76); }""")

    def color_picker(self):  # change color; update_style()
        if self.color != (0, 0, 0):  # (black doesnt work as initial color)
            self.color = QColorDialog.getColor(parent=self.parent().parent(),initial=QColor(*self.color)).getRgb()[:3]
        else:
            self.color = QColorDialog.getColor(parent=self.parent().parent()).getRgb()[:3]  # initial color = white
        self.update_style()

    def eventFilter(self, obj, event):  # -> left_mouse_click: select/ unselect | right_mouse_click: color_picker()
        if event.type() == QEvent.MouseButtonPress:
            if event.button() == Qt.LeftButton:
                self.setChecked(True)
            elif event.button() == Qt.RightButton:
                self.color_picker()
                # if main color --> gui update mainColor
                if self.name == "Color1/ Main Color" or self.name == "Farbe1/ Haupt-Farbe":
                    self.parent().parent().mainColor = self.color
        return QObject.event(obj, event)
# ----------------------------------------------------------------------------------------------------------------------
