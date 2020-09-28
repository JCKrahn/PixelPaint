<img src='img/logo.png' width='600'>

This is my first "real" project :)

[Download releases](https://github.com/juliuskrahn/PixelPaint/releases)

[PixelPaint website](https://pixelpaint.eu.pythonanywhere.com)


## Preview:
<img src='img/prev_img.PNG' width='600'>


## Building exe + exe-installer from source code:
### requires:
- PixelPaint source code
- Microsoft Visual C++ Redistributable Package ([x86](https://www.microsoft.com/en-us/download/details.aspx?id=29); [x64](https://www.microsoft.com/en-us/download/details.aspx?id=15336))
- Python2.7 
- python packages:
  - python-qt5 (v0.1.10)
  - pygame (v1.9.6)
  - pywin32 (v227)
  - numpy (v1.16.6)
  - opencv-python (v4.1.2.30)
  - pathlib2 (v2.3.5)
  - cx-Freeze (v5.1.1)
- Inno Setup Compiler (for building the PixelPaint installer)
  
### how to build exe + exe-installer from source code:
- run exe_setup.py 
- modify file paths in PixelPaint_installer_setup.iss
- run PixelPaint_installer_setup.iss with the Inno Setup Compiler
