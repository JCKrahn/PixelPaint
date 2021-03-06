import sys
import os
import pathlib2
from cx_Freeze import setup, Executable

sys.argv.append("build")


def delete_dir(path):
    for sub in path.iterdir():
        if sub.is_dir():
            delete_dir(sub)
        else:
            sub.unlink()
    path.rmdir()


if os.path.exists("build"):
    delete_dir(pathlib2.Path("build"))
    print "deleting directory: build"


setup(
    name="PixelPaint",
    version="1.1.0",
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
                                 "pathlib2",

                                 "main_win_process",
                                 "paint_win_process",
                                 "paint_win_image",
                                 "ini_manager",
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

    executables=[Executable(script="PixelPaint.py", base="win32GUI", icon="build_resources\\icon.ico")]
)


os.rename("build\\exe.win-amd64-2.7", "build\\exe")
print "renaming directory: build/exe.win-amd64-2.7 -> build/exe"

delete_dir(pathlib2.Path("build\\exe\\tcl"))  # (unnecessary file)
print "deleting directory: build/exe/tcl"

delete_dir(pathlib2.Path("build\\exe\\tk"))  # (unnecessary file)
print "deleting directory: build/exe/tk"

pathlib2.Path("build\\installer").mkdir()
print "creating directory: build/installer"
