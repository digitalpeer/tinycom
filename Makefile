RCC = pyrcc4 -py3

generated = tinycom/tinycom_rc.py

all: $(generated)

tinycom/%_rc.py: tinycom/res/%.qrc
	$(RCC) $< -o $@
# Get rid of the generated PyQt4 import and use our own wrapper
	sed -i 's/from PyQt4 import QtCore/from .qt import */' $@

LINT_FILES=tinycom/tinycom.py \
	tinycom/guisave.py \
	tinycom/serialthread.py

pylint:
	pylint --reports=n $(LINT_FILES)

pylint3:
	pylint3 --reports=n $(LINT_FILES)

clean:
	rm -f *.pyc tinycom/*.pyc $(generated)
	rm -rf dist build tinycom.egg-info

package: $(generated)
	python setup.py sdist
	python setup.py bdist_wheel
