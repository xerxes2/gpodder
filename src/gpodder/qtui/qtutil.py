# -*- coding: utf-8 -*-
#
# gPodder - A media aggregator and podcast client
# Copyright (c) 2005-2011 Thomas Perl and the gPodder Team
#
# gPodder is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# gPodder is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import absolute_import

import os.path
from sys import argv
from PySide  import QtCore
from PySide import QtGui

def get_file_from_filechooser(main, folder=False, save_file=False, save_to=None):
    filenames = None
    dialog = QtGui.QFileDialog(main.main_window)
    dialog.setDirectory(os.path.expanduser(main.config.get("options", "default_folder")))
    if not save_file:
        dialog.setFileMode(QtGui.QFileDialog.ExistingFile)
    if folder:
        dialog.setFileMode(QtGui.QFileDialog.Directory)
    if dialog.exec_():
       filenames = dialog.selectedFiles()
       main.config.set("options", "default_folder", dialog.directory().path())

    dialog.close()
    return filenames

def dialog(parent, text="", info="", ok=None, save=None, cancel=None, discard=None):
    msgBox = QtGui.QMessageBox(parent)
    msgBox.setText(text.decode("utf-8"))
    msgBox.setInformativeText(info.decode("utf-8"))
    if save and cancel and discard:
        msgBox.setStandardButtons(QtGui.QMessageBox.Cancel | QtGui.QMessageBox.Discard | QtGui.QMessageBox.Save )
    elif ok and cancel and discard:
        msgBox.setStandardButtons(QtGui.QMessageBox.Cancel | QtGui.QMessageBox.Discard | QtGui.QMessageBox.Ok )
    elif save and cancel:
        msgBox.setStandardButtons(QtGui.QMessageBox.Cancel | QtGui.QMessageBox.Save )
    elif ok and cancel:
        msgBox.setStandardButtons(QtGui.QMessageBox.Cancel | QtGui.QMessageBox.Ok )
    else:
        msgBox.setStandardButtons(QtGui.QMessageBox.Close )

    response = msgBox.exec_()
    return response

def find_data_file(filename):
    bin_dir = os.path.dirname(argv[0])
    locations = [
            os.path.join(bin_dir, '..', 'share', 'gpodder'),
            os.path.join(bin_dir, '..', 'icons'),
            os.path.join(bin_dir, '..', 'data'),
            '/opt/gpodder',
    ]

    for location in locations:
        fn = os.path.abspath(os.path.join(location, filename))
        if os.path.exists(fn):
            return fn
