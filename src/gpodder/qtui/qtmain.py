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

import logging
import os.path
import cgi
import gobject
from PySide  import QtCore
from PySide import QtGui

try:
    import pynotify
    pynotify.init('gPodder')
    have_pynotify = True
except:
    have_pynotify = False

try:
    import dbus
    import dbus.service
    import dbus.mainloop
    import dbus.glib
except ImportError:
    # Mock the required D-Bus interfaces with no-ops (ugly? maybe.)
    class dbus:
        class SessionBus:
            def __init__(self, *args, **kwargs):
                pass
            def add_signal_receiver(self, *args, **kwargs):
                pass
        class glib:
            class DBusGMainLoop:
                def __init__(self, *args, **kwargs):
                    pass
        class service:
            @staticmethod
            def method(*args, **kwargs):
                return lambda x: x
            class BusName:
                def __init__(self, *args, **kwargs):
                    pass
            class Object:
                def __init__(self, *args, **kwargs):
                    pass

import gpodder
from gpodder import feedcore
from gpodder import util
from gpodder import opml
from gpodder import download
from gpodder import my
from gpodder import youtube
from gpodder import player
from gpodder.liblogger import log

_ = gpodder.gettext
N_ = gpodder.ngettext

from gpodder.model import PodcastChannel
from gpodder.model import PodcastEpisode
from gpodder.dbsqlite import Database

from gpodder.qtui.qtconfig import UIConfig

class gPodder():
    def __init__(self, bus_name, config):
        self.config = config
        #print self.config
        self.app = QtGui.QApplication(["gPodder"])
        self.app.setWindowIcon(QtGui.QIcon('/usr/share/icons/hicolor/24x24/apps/gpodder.png'))
        self.main_window = QtGui.QMainWindow(None)
        if gpodder.ui.fremantle:
            self.main_window.setAttribute(QtCore.Qt.WA_Maemo5StackedWindow)
        self.main_window.closeEvent = self.close_main_window_callback
        self.create_actions()
        if gpodder.ui.fremantle:
            self.create_handset_menus()
        else:
            self.create_menus()
        widget = QtGui.QWidget()
        self.main_window.setCentralWidget(widget)
        layout = QtGui.QVBoxLayout()
        widget.setLayout(layout)
        layout.addWidget(self.create_toolbar())
        self.podcaststab = PodcastsTab(self)
        self.downloadstab = DownloadsTab(self)
        tw = QtGui.QTabWidget()
        tw.addTab(self.podcaststab.splitter, _("Podcasts"))
        tw.addTab(self.downloadstab.main_widget, _("Downloads"))
        layout.addWidget(tw)
        self.main_window.show()
        if not self.config["show_toolbar"]:
            self.toolbar.hide()
        self.app.exec_()

    def create_actions(self):
        # Podcasts menu
        self.action_check_episodes = QtGui.QAction(QtGui.QIcon(''), _("Check for new episodes").decode("utf-8"), self.main_window,
            shortcut="Ctrl+R", triggered=self.quit_app)
        self.action_download_episodes = QtGui.QAction(QtGui.QIcon('/usr/share/icons/gnome/16x16/actions/go-bottom.png'),
            _("Download new episodes").decode("utf-8"), self.main_window, shortcut="Ctrl+N", triggered=self.quit_app)
        self.action_delete_episodes = QtGui.QAction(QtGui.QIcon(''), _("Delete episodes").decode("utf-8"), self.main_window,
            shortcut="Ctrl+K", triggered=self.quit_app)
        self.action_preferences = QtGui.QAction(QtGui.QIcon('/usr/share/icons/gnome/16x16/categories/gtk-preferences.png'),
            _("Preferences").decode("utf-8"), self.main_window, shortcut="Ctrl+P", triggered=self.preferences_callback)
        self.action_quit = QtGui.QAction(QtGui.QIcon('/usr/share/icons/gnome/16x16/actions/exit.png'), _("Quit").decode("utf-8"), self.main_window,
            shortcut="Ctrl+Q", statusTip="Exit the application", triggered=self.quit_app)
        # Subscriptions menu
        self.action_discover_podcasts = QtGui.QAction(QtGui.QIcon(''), _("Discover new podcasts").decode("utf-8"), self.main_window,
            shortcut="Ctrl+F", triggered=self.quit_app)
        self.action_add_podcast = QtGui.QAction(QtGui.QIcon(''), _("Add podcast via URL").decode("utf-8"), self.main_window,
            shortcut="Ctrl+L", triggered=self.quit_app)
        self.action_remove_podcasts = QtGui.QAction(QtGui.QIcon(''), _("Remove podcasts").decode("utf-8"), self.main_window,
            triggered=self.quit_app)
        self.action_update_podcast = QtGui.QAction(QtGui.QIcon(''), _("Update podcast").decode("utf-8"), self.main_window,
            triggered=self.quit_app)
        self.action_import_opml = QtGui.QAction(QtGui.QIcon(''), _("Import from OPML file").decode("utf-8"), self.main_window,
            shortcut="Ctrl+O", triggered=self.quit_app)
        self.action_export_opml = QtGui.QAction(QtGui.QIcon(''), _("Export to OPML file").decode("utf-8"), self.main_window,
            triggered=self.quit_app)
        # Episodes menu
        self.action_play = QtGui.QAction(QtGui.QIcon('/usr/share/icons/gnome/16x16/actions/gtk-media-play-ltr.png'), _("Play").decode("utf-8"), self.main_window,
            shortcut="Shift+Return", triggered=self.quit_app)
        self.action_download = QtGui.QAction(QtGui.QIcon('/usr/share/icons/gnome/16x16/actions/go-bottom.png'),
            _("Download").decode("utf-8"), self.main_window, triggered=self.quit_app)
        self.action_cancel = QtGui.QAction(QtGui.QIcon('/usr/share/icons/gnome/16x16/actions/gtk-cancel.png'),
            _("Cancel").decode("utf-8"), self.main_window, triggered=self.quit_app)
        self.action_delete = QtGui.QAction(QtGui.QIcon('/usr/share/icons/gnome/16x16/actions/gtk-delete.png'),
            _("Delete").decode("utf-8"), self.main_window, shortcut="Delete", triggered=self.quit_app)
        self.action_change_status = QtGui.QAction(QtGui.QIcon(''), _("Change played status").decode("utf-8"), self.main_window,
            triggered=self.quit_app)
        self.action_change_lock = QtGui.QAction(QtGui.QIcon(''), _("Change delete lock").decode("utf-8"), self.main_window,
            triggered=self.quit_app)
        self.action_episode_details = QtGui.QAction(QtGui.QIcon(''), _("Episode details").decode("utf-8"), self.main_window,
            triggered=self.quit_app)
        # View menu
        self.action_podcast_list = QtGui.QAction(QtGui.QIcon(''), _("Podcast list").decode("utf-8"), self.main_window,
            shortcut="F9", triggered=self.podcast_list_callback)
        self.action_podcast_list.setCheckable(True)
        self.action_podcast_list.setChecked(True)
        self.action_all_podcast_list = QtGui.QAction(QtGui.QIcon(''), _('"All episodes" in podcast list').decode("utf-8"), self.main_window,
            triggered=self.all_podcast_list_callback)
        self.action_all_podcast_list.setCheckable(True)
        if self.config["podcast_list_view_all"]:
            self.action_all_podcast_list.setChecked(True)
        self.action_toolbar = QtGui.QAction(QtGui.QIcon(''), _("Toolbar").decode("utf-8"), self.main_window,
            shortcut="Ctrl+T", triggered=self.toolbar_callback)
        self.action_toolbar.setCheckable(True)
        if self.config["show_toolbar"]:
            self.action_toolbar.setChecked(True)
        self.action_episode_descriptions = QtGui.QAction(QtGui.QIcon(''), _("Episode descriptions").decode("utf-8"), self.main_window,
            shortcut="Ctrl+D", triggered=self.episode_descriptions_callback)
        self.action_episode_descriptions.setCheckable(True)
        if self.config["episode_list_descriptions"]:
            self.action_episode_descriptions.setChecked(True)
        self.action_all_episodes = QtGui.QAction(QtGui.QIcon(''), _("All episodes").decode("utf-8"), self.main_window,
            shortcut="Ctrl+0", triggered=self.all_episodes_callback)
        self.action_all_episodes.setCheckable(True)
        self.action_hide_deleted = QtGui.QAction(QtGui.QIcon(''), _("Hide deleted episodes").decode("utf-8"), self.main_window,
            shortcut="Ctrl+1", triggered=self.hide_deleted_callback)
        self.action_hide_deleted.setCheckable(True)
        self.action_downloaded_episodes = QtGui.QAction(QtGui.QIcon(''), _("Downloaded episodes").decode("utf-8"), self.main_window,
            shortcut="Ctrl+2", triggered=self.downloaded_episodes_callback)
        self.action_downloaded_episodes.setCheckable(True)
        self.action_deleted_episodes = QtGui.QAction(QtGui.QIcon(''), _("Deleted episodes").decode("utf-8"), self.main_window,
            shortcut="Ctrl+3", triggered=self.deleted_episodes_callback)
        self.action_deleted_episodes.setCheckable(True)
        actiongroup = QtGui.QActionGroup(self.main_window)
        actiongroup.setExclusive(True)
        self.action_all_episodes.setActionGroup(actiongroup)
        self.action_hide_deleted.setActionGroup(actiongroup)
        self.action_downloaded_episodes.setActionGroup(actiongroup)
        self.action_deleted_episodes.setActionGroup(actiongroup)
        if self.config["episode_list_view_mode"] == 0:
            self.action_all_episodes.setChecked(True)
        elif self.config["episode_list_view_mode"] == 1:
            self.action_hide_deleted.setChecked(True)
        elif self.config["episode_list_view_mode"] == 2:
            self.action_downloaded_episodes.setChecked(True)
        else:
            self.action_deleted_episodes.setChecked(True)
        self.action_without_episodes = QtGui.QAction(QtGui.QIcon(''), _("Hide podcasts without episodes").decode("utf-8"), self.main_window,
            triggered=self.without_episodes_callback)
        self.action_without_episodes.setCheckable(True)
        if self.config["podcast_list_hide_boring"]:
            self.action_without_episodes.setChecked(True)
        self.action_size = QtGui.QAction(QtGui.QIcon(''), _("Size").decode("utf-8"), self.main_window,
            triggered=self.visible_columns_callback)
        self.action_size.setCheckable(True)
        self.action_duration = QtGui.QAction(QtGui.QIcon(''), _("Duration").decode("utf-8"), self.main_window,
            triggered=self.visible_columns_callback)
        self.action_duration.setCheckable(True)
        self.action_released = QtGui.QAction(QtGui.QIcon(''), _("Released").decode("utf-8"), self.main_window,
            triggered=self.visible_columns_callback)
        self.action_released.setCheckable(True)
        _int = self.config["episode_list_columns"]
        if _int == 1 or _int == 3 or _int == 5 or _int == 7:
            self.action_size.setChecked(True)
        if _int == 2 or _int == 3 or _int > 5:
            self.action_duration.setChecked(True)
        if _int > 3:
            self.action_released.setChecked(True)
        # Help menu
        self.action_user_manual = QtGui.QAction(QtGui.QIcon(''), _("User manual").decode("utf-8"), self.main_window,
            shortcut="Ctrl+H", triggered=self.user_manual_callback)
        self.action_homepage = QtGui.QAction(QtGui.QIcon(''), _("Go to gpodder.net").decode("utf-8"), self.main_window,
            triggered=self.homepage_callback)
        self.action_about = QtGui.QAction(QtGui.QIcon('about.png'), _("About").decode("utf-8"), self.main_window,
            statusTip="Show about dialog", triggered=self.about_callback)

    def create_menus(self):
        # Podcasts menu
        menu = self.main_window.menuBar().addMenu(_("Podcasts").decode("utf-8"))
        menu.addAction(self.action_check_episodes)
        menu.addAction(self.action_download_episodes)
        menu.addAction(self.action_delete_episodes)
        menu.addSeparator()
        menu.addAction(self.action_preferences)
        menu.addSeparator()
        menu.addAction(self.action_quit)
        # Subscriptions menu
        menu = self.main_window.menuBar().addMenu(_("Subscriptions").decode("utf-8"))
        menu.addAction(self.action_discover_podcasts)
        menu.addAction(self.action_add_podcast)
        menu.addAction(self.action_remove_podcasts)
        menu.addSeparator()
        menu.addAction(self.action_update_podcast)
        menu.addSeparator()
        menu.addAction(self.action_import_opml)
        menu.addAction(self.action_export_opml)
        # Episodes menu
        menu = self.main_window.menuBar().addMenu(_("Episodes").decode("utf-8"))
        menu.addAction(self.action_play)
        menu.addAction(self.action_download)
        menu.addAction(self.action_cancel)
        menu.addAction(self.action_delete)
        menu.addSeparator()
        menu.addAction(self.action_change_status)
        menu.addAction(self.action_change_lock)
        menu.addSeparator()
        menu.addAction(self.action_episode_details)
        # View menu
        menu = self.main_window.menuBar().addMenu(_("View").decode("utf-8"))
        menu.addAction(self.action_podcast_list)
        menu.addAction(self.action_all_podcast_list)
        menu.addSeparator()
        menu.addAction(self.action_toolbar)
        menu.addAction(self.action_episode_descriptions)
        menu.addSeparator()
        menu.addAction(self.action_all_episodes)
        menu.addAction(self.action_hide_deleted)
        menu.addAction(self.action_downloaded_episodes)
        menu.addAction(self.action_deleted_episodes)
        menu.addSeparator()
        menu.addAction(self.action_without_episodes)
        menu.addSeparator()
        submenu = menu.addMenu(_("Visible columns").decode("utf-8"))
        submenu.addAction(self.action_size)
        submenu.addAction(self.action_duration)
        submenu.addAction(self.action_released)
        # Help menu
        menu = self.main_window.menuBar().addMenu(_("Help").decode("utf-8"))
        menu.addAction(self.action_user_manual)
        menu.addAction(self.action_homepage)
        menu.addSeparator()
        menu.addAction(self.action_about)

    def create_handset_menus(self):
        # Main window
        self.menu_player = self.main_window.menuBar().addMenu("")
        self.menu_player.addAction(self.action_about)

    def create_toolbar(self):
        self.toolbar = QtGui.QToolBar()
        self.toolbar.addAction(self.action_download)
        self.toolbar.addAction(self.action_play)
        self.toolbar.addAction(self.action_cancel)
        self.toolbar.addAction(self.action_preferences)
        self.toolbar.addAction(self.action_quit)
        return self.toolbar

    def preferences_callback(self):
        from gpodder.qtui.qtsettingsdialog import SettingsDialog
        SettingsDialog(self)

    def quit_app(self):
        self.main_window.hide()
        self.config.save()
        self.app.exit()

    def close_main_window_callback(self, event):
        self.quit_app()

    def show_main_window(self):
        self.main_window.activateWindow()

    def podcast_list_callback(self):
        if self.action_podcast_list.isChecked():
            self.podcaststab.podcast_list.show()
        else:
            self.podcaststab.podcast_list.hide()

    def all_podcast_list_callback(self):
        if self.action_all_podcast_list.isChecked():
            pass
        else:
            pass
        self.config["podcast_list_view_all"] = self.action_all_podcast_list.isChecked()

    def toolbar_callback(self):
        if self.action_toolbar.isChecked():
            self.toolbar.show()
        else:
            self.toolbar.hide()
        self.config["show_toolbar"] = self.action_toolbar.isChecked()

    def episode_descriptions_callback(self):
        if self.action_episode_descriptions.isChecked():
            pass
        else:
            pass
        self.config["episode_list_descriptions"] = self.action_episode_descriptions.isChecked()
        
    def all_episodes_callback(self):
        self.config["episode_list_view_mode"] = 0

    def hide_deleted_callback(self):
        self.config["episode_list_view_mode"] = 1

    def downloaded_episodes_callback(self):
        self.config["episode_list_view_mode"] = 2

    def deleted_episodes_callback(self):
        self.config["episode_list_view_mode"] = 3

    def without_episodes_callback(self):
        if self.action_without_episodes.isChecked():
            pass
        else:
            pass
        self.config["podcast_list_hide_boring"] = self.action_without_episodes.isChecked()

    def visible_columns_callback(self):
        _int = 0
        if self.action_size.isChecked():
            _int+=1
        if self.action_duration.isChecked():
            _int+=2
        if self.action_released.isChecked():
            _int+=4
        self.config["episode_list_columns"] = _int

    def user_manual_callback(self):
        os.system("xdg-open http://wiki.gpodder.org/wiki/User_Manual")

    def homepage_callback(self):
        os.system("xdg-open http://gpodder.net")

    def about_callback(self):
        from gpodder.qtui import qtaboutdialog
        qtaboutdialog.AboutDialog(self.main_window)

class PodcastsTab():
    def __init__(self, main):
        self.__main = main
        self.splitter =  QtGui.QSplitter()
        self.podcast_list = QtGui.QWidget()
        vlayout = QtGui.QVBoxLayout()
        self.podcast_list.setLayout(vlayout)
        self.splitter.addWidget(self.podcast_list)
        lw = QtGui.QListView()
        vlayout.addWidget(lw)
        button = QtGui.QPushButton(QtGui.QIcon("/usr/share/icons/gnome/24x24/actions/reload.png"), _("Check for Updates"))
        vlayout.addWidget(button)
        lw = QtGui.QListView()
        self.splitter.addWidget(lw)

class DownloadsTab():
    def __init__(self, main):
        self.__main = main
        self.main_widget = QtGui.QWidget()
        self.main_layout = QtGui.QVBoxLayout()
        self.main_widget.setLayout(self.main_layout)
        lw = QtGui.QListView()
        self.main_layout.addWidget(lw)
        hlayout = QtGui.QHBoxLayout()
        self.main_layout.addLayout(hlayout)
        box_rate = QtGui.QCheckBox(_("Limit rate to").decode("utf-8"))
        hlayout.addWidget(box_rate)
        le = QtGui.QLineEdit()
        hlayout.addWidget(le)
        label = QtGui.QLabel("KiB/s")
        hlayout.addWidget(label)
        hlayout.addStretch(2)
        box_downloads = QtGui.QCheckBox(_("Limit downloads to").decode("utf-8"))
        hlayout.addWidget(box_downloads)
        le = QtGui.QLineEdit()
        hlayout.addWidget(le)
        le.setMaxLength(2)


def main(options=None):
    gobject.threads_init()
    gobject.set_application_name('gPodder')

    dbus_main_loop = dbus.glib.DBusGMainLoop(set_as_default=True)
    gpodder.dbus_session_bus = dbus.SessionBus(dbus_main_loop)
    bus_name = dbus.service.BusName(gpodder.dbus_bus_name, bus=gpodder.dbus_session_bus)

    util.make_directory(gpodder.home)
    gpodder.load_plugins()

    config = UIConfig(gpodder.config_file)

    """
    # Load hook modules and install the hook manager globally
    # if modules have been found an instantiated by the manager
    user_hooks = hooks.HookManager()
    if user_hooks.has_modules():
        gpodder.user_hooks = user_hooks

 
    if config.enable_fingerscroll:
        BuilderWidget.use_fingerscroll = True

    config.mygpo_device_type = util.detect_device_type()
    """
    gp = gPodder(bus_name, config)
    """
    # Handle options
    if options.subscribe:
        util.idle_add(gp.subscribe_to_url, options.subscribe)

    # mac OS X stuff :
    # handle "subscribe to podcast" events from firefox
    if platform.system() == 'Darwin':
        from gpodder import gpodderosx
        gpodderosx.register_handlers(gp)
    # end mac OS X stuff

    gp.run()
    """
