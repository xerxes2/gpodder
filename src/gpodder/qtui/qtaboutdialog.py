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

class AboutDialog:
    def __init__(self, parent):
        self.ad = QtGui.QDialog(parent)
        self.ad.setWindowTitle(_("About").decode("utf-8"))
        main_layout = QtGui.QVBoxLayout()
        self.ad.setLayout(main_layout)

        hlayout = QtGui.QHBoxLayout()
        label = QtGui.QLabel()
        pixmap = QtGui.QPixmap('/usr/share/icons/hicolor/48x48/apps/gpodder.png')
        label.setPixmap(pixmap)
        hlayout.addWidget(label)

        vlayout = QtGui.QVBoxLayout()
        label = QtGui.QLabel()
        label.setText('<b><big>' + about.about_name + " " +  gpodder.__version__ + '</b></big>')
        vlayout.addWidget(label, 2)
        label = QtGui.QLabel()
        label.setText(about.about_text.decode("utf-8"))
        vlayout.addWidget(label, 2)
        label = QtGui.QLabel(about.about_copyright)
        vlayout.addWidget(label, 2)
        label = QtGui.QLabel("<qt><a href='%s'>"%(about.about_website) + about.about_website + "</a></qt>")
        label.setOpenExternalLinks(True)
        vlayout.addWidget(label, 2)
        hlayout.addLayout(vlayout, 2)
        main_layout.addLayout(hlayout)

        layout = QtGui.QHBoxLayout()
        layout.addStretch(2)
        button = QtGui.QPushButton(_("Credits").decode("utf-8"))
        button.clicked.connect(self.show_credits)
        layout.addWidget(button)
        button = QtGui.QPushButton(_("Close").decode("utf-8"))
        button.clicked.connect(self.close)
        layout.addWidget(button)
        main_layout.addLayout(layout)

        self.cd = QtGui.QDialog(self.ad)
        self.cd.setWindowTitle(_("Credits").decode("utf-8"))
        self.cd.setModal(True)
        layout = QtGui.QVBoxLayout()
        self.cd.setLayout(layout)

        tw = QtGui.QTabWidget()
        layout.addWidget(tw)
        te = QtGui.QTextEdit()
        tw.addTab(te, _("Authors").decode("utf-8"))
        te.setReadOnly(True)
        _str = ""
        for i in about.about_authors:
            _str = _str + i + "\n"
        te.setPlainText(_str.decode("utf-8"))
        te = QtGui.QTextEdit()
        tw.addTab(te, _("Contributors").decode("utf-8"))
        te.setReadOnly(True)
        _str = ""
        for i in about.about_contributors:
            _str = _str + i + "\n"
        te.setPlainText(_str.decode("utf-8"))

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
        self.cd.show()

    def close_credits(self):
        self.cd.close()
