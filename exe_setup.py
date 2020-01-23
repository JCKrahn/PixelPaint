"""
EXE Setup

# -> : pipenv run python exe_setup.py build
# rename build/exe.win-amd64-2.7 to exe
# remove build/exe/tcl, build/exe/tk
# create folder build/exe/include
# move folders from build/exe/* to build/exe/include
# create folder build/installer
# open PixelPaint_installer_setup with InnoSetupCompiler
# run PixelPaint_installer_setup
"""

from cx_Freeze import setup, Executable

setup(
    name="PixelPaint",
    version="1.0",
    options={"build_exe":{"packages":
                                ["sys",
                                 "os",
                                 "time",
                                 "multiprocessing",
                                 "win32gui",
                                 "numpy",
                                 "cv2",
                                 "pygame",
                                 "webbrowser",
                                 "gui_classes",
                                 "paint_process",
                                 "ini_manager",
                                 "pathlib2",
                                 "language"],
                            "include_files":
                                ["data"],
                            "excludes":
                            ["json",
                             "xml",
                             "email",
                             "pydoc_data",
                             "test",
                             "logging"]
                            }},
    executables=[Executable(script="PixelPaint.py", base = "win32GUI", icon="build_resources\icon.ico")]
)
