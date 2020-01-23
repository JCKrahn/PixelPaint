# -*- coding: utf-8 -*-
"""
GUI Classes
"""

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *


# pop up windows -------------------------------------------------------------------------------------------------------
class GeneralSettingsMenu(QDialog):
    def __init__(self, parent, ini, lang):
        super(GeneralSettingsMenu, self).__init__(parent, Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        self.setWindowTitle(lang["general settings"])
        self.setFixedSize(200, 110)

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
        self.setFixedSize(230, 220)

        self.ini = ini
        self.lang = lang

        mainLayout = QVBoxLayout()

        spacer_item = QSpacerItem(220, 10, QSizePolicy.Minimum, QSizePolicy.Expanding)

        # Fill Tool Settings ------------------------------------------------------
        fill_tool_settings_group = QGroupBox()
        fill_tool_settings_group.setTitle(lang["fill tool settings"])
        fill_tool_settings_layout = QVBoxLayout()

        fill_alg_visual_button_layout = QHBoxLayout()
        fill_alg_visual_button_txt = QLabel()
        fill_alg_visual_button_txt.setText(lang["visualize fill algorithm"])
        fill_alg_visual_button_layout.addWidget(fill_alg_visual_button_txt)
        self.fill_alg_visual_button = QRadioButton()
        if ini["fill_alg_visual"] == "true": self.fill_alg_visual_button.setChecked(True)
        fill_alg_visual_button_layout.addWidget(self.fill_alg_visual_button)
        fill_tool_settings_layout.addLayout(fill_alg_visual_button_layout)
        fill_tool_settings_layout.addItem(spacer_item)

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
                message = Message(self, (284, 86), self.lang["paintwindow settings"],
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
        if self.fill_alg_visual_button.isChecked(): self.ini["fill_alg_visual"] = "true"
        else: self.ini["fill_alg_visual"] = "false"
        if self.fill_tool_tolerance_group.isChecked(): self.ini["enable_fill_alg_tolerance"] = "true"
        else: self.ini["enable_fill_alg_tolerance"] = "false"
        self.ini["fill_alg_tolerance"] = self.set_fill_tool_tolerance.text()
        if self.image_maxsize_button.isChecked(): self.ini["image_loader_maxsize"] = "true"
        else: self.ini["image_loader_maxsize"] = "false"

        self.done(1)


class NewProjectConfigPrompt(QDialog):
    def __init__(self, parent, lang):
        self.lang = lang
        # standard values
        self.config_width = "64"
        self.config_height = "64"
        self.config_background = (255, 255, 255, 0)
        # -------------------------
        super(NewProjectConfigPrompt, self).__init__(parent)

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
    def __init__(self, parent, size, title, text):
        super(ErrorMessage, self).__init__(parent, Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        self.setWindowTitle(title)
        self.setWindowIcon(QIcon("data/icons/error.png"))
        self.setFixedSize(*size)
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
    def __init__(self, parent, size, title, text):
        super(Message, self).__init__(parent, Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        self.setWindowTitle(title)
        self.setWindowIcon(QIcon("data/icons/icon.png"))
        self.setFixedSize(*size)
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
    def __init__(self, parent, size, title, text, close_button_text, cancel_button_text):
        super(CloseWarning, self).__init__(parent, Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        self.setWindowTitle(title)
        self.setWindowIcon(QIcon("data/icons/icon.png"))
        self.setFixedSize(*size)
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

    def color_picker(self):  # pick color via ColorDialog; update_style()
        self.color = QColorDialog.getColor().getRgb()[:3]
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
