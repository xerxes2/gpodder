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
from PySide  import QtCore
from PySide import QtGui

import gpodder
from gpodder import about
_ = gpodder.gettext

class SettingsDialog:
    def __init__(self, main):
        self.__main = main
        self.ad = QtGui.QDialog(self.__main.main_window)
        self.ad.setWindowTitle(_("Preferences").decode("utf-8"))
        main_layout = QtGui.QVBoxLayout()
        self.ad.setLayout(main_layout)

        tw = QtGui.QTabWidget()
        main_layout.addWidget(tw)

        widget = QtGui.QWidget()
        layout = QtGui.QVBoxLayout()
        widget.setLayout(layout)
        tw.addTab(widget, _("General").decode("utf-8"))

        widget = QtGui.QWidget()
        layout = QtGui.QVBoxLayout()
        widget.setLayout(layout)
        tw.addTab(widget, _("gpodder.net").decode("utf-8"))

        widget = QtGui.QWidget()
        layout = QtGui.QVBoxLayout()
        widget.setLayout(layout)
        tw.addTab(widget, _("Updating").decode("utf-8"))

        widget = QtGui.QWidget()
        layout = QtGui.QVBoxLayout()
        widget.setLayout(layout)
        tw.addTab(widget, _("Clean-up").decode("utf-8"))

        layout = QtGui.QHBoxLayout()
        layout.addStretch(2)
        button = QtGui.QPushButton(_("Edit config").decode("utf-8"))
        button.clicked.connect(self.show_credits)
        layout.addWidget(button)
        button = QtGui.QPushButton(_("Close").decode("utf-8"))
        button.clicked.connect(self.close)
        layout.addWidget(button)
        main_layout.addLayout(layout)

        self.ce = QtGui.QDialog(self.ad)
        self.ce.setWindowTitle(_("gPodder Configuration Editor").decode("utf-8"))
        self.ce.setModal(True)
        layout = QtGui.QVBoxLayout()
        self.ce.setLayout(layout)

        hlayout = QtGui.QHBoxLayout()
        hlayout.addStretch(2)
        button = QtGui.QPushButton(_("Close").decode("utf-8"))
        button.clicked.connect(self.close_credits)
        hlayout.addWidget(button)

        layout.addLayout(hlayout)
        self.ad.exec_()

    def close(self):
        self.ad.close()

    def show_credits(self):
        self.ce.show()

    def close_credits(self):
        self.ce.close()
