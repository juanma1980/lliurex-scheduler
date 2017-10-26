#!/bin/bash

PYTHON_FILES="../scheduler-gui.install/usr/share/taskscheduler/bin/taskScheduler.py ../python3-taskscheduler.install/usr/share/taskscheduler/*.py"
UI_FILES="../scheduler-gui.install/usr/share/taskscheduler/rsrc/taskScheduler.ui"

mkdir -p taskscheduler/

xgettext $UI_FILES $PYTHON_FILES -o taskscheduler/taskscheduler.pot


