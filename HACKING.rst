Developer Notes
===============
The UI is built with QT Designer.  The resulting *.ui is then loaded at runtime
to create the UI.  In any event, this should provide all tools on Ubuntu.

Install PyQt or PySide tools.

    sudo apt-get install {pyqt4-dev-tools|pyside-tools}

The rest of the necessary tools.

    sudo apt-get install python qt4-designer python-setuptools python-pip

Other than that, use your favorite editor.  Here's how you install that.

    sudo apt-get install emacs

Back at the top level, run make, then run the tinycom package directly using:

    python -m tinycom

Or install in development mode using one of:

    pip install --user [--no-index] --editable .
    python setup.py develop --user

This will give you a `tinycom` target to run.

Windows
-------
Download and install Python.
Add C:\Python27\ to system Path variable.
Download and install pip.
Add C:\Python27\Scripts to system Path variable.
Fire up a win32 command prompt.

    pip install pyinstaller
    pip install pyserial
    pip install PySide

Now you can just run tinycom.

PyInstaller
===========

    python -m tinycom
    pyinstaller tinycom.spec

PyQt4/PyQt5/PySide
------------------
See the note in the `README.md` about PyQt vs. PySide. Both are supported at
runtime with ''qt.py'' import abstraction.


Release Process
---------------

* Update __version__ in __init__.py
* Update CHANGES.rst
* Push version tag
* make clean; make package; sign and upload
