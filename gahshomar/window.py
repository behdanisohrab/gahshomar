# -*- Mode: Python; coding: utf-8; indent-tabs-mode: s; tab-width: 4 -*-
#
# Copyright (C) 2014 Amir Mohammadi <183.amir@gmail.com>
#
# Gahshomar is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Gahshomar is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.

import datetime
from gettext import gettext as _
import logging
logger = logging.getLogger(__name__)

from gi.repository import Gtk, Gio, GLib

import gahshomar.widgets as Widgets
# from gahshomar.plugin_manager import GSPluginManager
from gahshomar import log


class Window(Gtk.ApplicationWindow):

    @log
    def __init__(self, app):
        self.app = app
        Gtk.ApplicationWindow.__init__(self,
                                       application=app,
                                       title=_("Gahshomar"))
        self.date = datetime.date.today()
        # self.connect('focus-in-event', self._windows_focus_cb)
        self.settings = Gio.Settings.new('org.gahshomar.Gahshomar')
        # self.add_action(self.settings.create_action('repeat'))
        # selectAll = Gio.SimpleAction.new('selectAll', None)
        # app.add_accelerator('<Primary>a', 'win.selectAll', None)
        # selectAll.connect('activate', self._on_select_all)
        # self.add_action(selectAll)
        # selectNone = Gio.SimpleAction.new('selectNone', None)
        # selectNone.connect('activate', self._on_select_none)
        # self.add_action(selectNone)
        self.set_size_request(200, 100)
        self.set_icon_name('gahshomar')

        size_setting = self.settings.get_value('window-size')
        if isinstance(size_setting[0], int) \
           and isinstance(size_setting[1], int):
            self.resize(size_setting[0], size_setting[1])

        position_setting = self.settings.get_value('window-position')
        if len(position_setting) == 2 \
           and isinstance(position_setting[0], int) \
           and isinstance(position_setting[1], int):
            self.move(position_setting[0], position_setting[1])

        if self.settings.get_value('window-maximized'):
            self.maximize()

        self.connect("window-state-event", self._on_window_state_event)
        self.connect("configure-event", self._on_configure_event)
        self.connect("delete-event", self.toggle_main_win)
        # set the icon for the window
        self.connect('style-set', self.set_icon_)
        self._setup_view()

        self.show_all()

    @log
    def _on_configure_event(self, widget, event):
        size = widget.get_size()
        self.settings.set_value(
            'window-size', GLib.Variant('ai', [size[0], size[1]]))

        position = widget.get_position()
        self.settings.set_value(
            'window-position', GLib.Variant('ai', [position[0], position[1]]))

    @log
    def _on_window_state_event(self, widget, event):
        self.settings.set_boolean(
            'window-maximized',
            'GDK_WINDOW_STATE_MAXIMIZED' in event.new_window_state.value_names)

    @log
    def _setup_view(self):
        pday = Widgets.PersianDayWidget(date=self.date, app=self.app)
        gday = Widgets.GeorgianDayWidget(date=self.date, app=self.app)
        self.day_widgets = [pday, gday]

        pcal = Widgets.PersianCalendarWidget(date=self.date, app=self.app)
        gcal = Widgets.GeorgianCalendarWidget(date=self.date, app=self.app)
        self.calendars = [pcal, gcal]

        self.handler = self.app.handler

        self.main_grid = Gtk.Grid()
        self.main_grid.show_all()
        self.add(self.main_grid)
        self.main_grid.set_column_homogeneous(True)
        self.main_grid.set_column_spacing(spacing=18)
        self.main_grid.set_row_spacing(spacing=18)

        self.offset = 0
        for i, v in enumerate(self.day_widgets):
            self.main_grid.attach(v, i, 0 + self.offset, 1, 1)
        for i, v in enumerate(self.calendars):
            self.main_grid.attach(v, i, 1 + self.offset, 1, 1)

       # setup appindicator
        self.visible = True
        # self.setup_appindicator()

        # check if unity is running
        # import os
        # xdg_current_desktop = os.environ.get('XDG_CURRENT_DESKTOP').lower()
        # self.xdg_current_desktop = xdg_current_desktop
        self.setup_header_bar()

        # update interface every 5 seconds
        # GLib.timeout_add_seconds(int(self.config['Global']['ping_frequency']),
        #                          self.handler.update_everything)


        # # finally load the plugins
        # try:
        #     self.plugin_manager = GSPluginManager(self)
        # except Exception:
        #     logger.exception(Exception)

    @log
    def setup_header_bar(self):
        # xdg_current_desktop = self.xdg_current_desktop
        today_button = Gtk.Button(label=_('Today'))
        today_button.connect("clicked", self.set_today)
        close_button = Gtk.Button.new_from_icon_name(
            'window-close-symbolic', Gtk.IconSize.BUTTON)
        close_button.connect('clicked', self.toggle_main_win)

        if False:  # 'unity' in xdg_current_desktop:
            toolbar = Gtk.Toolbar()
            sep = Gtk.SeparatorToolItem()
            sep.set_expand(True)
            sep.set_draw(False)
            toolbar.add(sep)
            tb_today = Gtk.ToolButton.new(today_button)
            tb_today.connect("clicked", self.set_today)
            toolbar.add(tb_today)
            # tb_close = Gtk.ToolButton.new(close_button)
            # tb_close.connect('clicked', self.toggle_main_win)
            # toolbar.add(tb_close)
            self.main_grid.attach(toolbar, 0, 0, 2, 1)
        else:
            # set header bar
            self.hb = Gtk.HeaderBar()
            self.hb.props.title = _('Gahshomar')
            self.hb.props.show_close_button = True

            # if USE_IND:
            #     self.hb.props.show_close_button = False
            #     self.hb.pack_end(close_button)
            # else:
            #     self.hb.props.show_close_button = True

            self.hb.pack_start(today_button)

            self.set_titlebar(self.hb)

    @log
    def set_today(self, *args):
        self.handler.update_everything(date=datetime.date.today())

    @log
    def toggle_main_win(self, *args):
        # if not USE_IND:
        #     return

        if self.visible:
            self.hide()
            self.visible = False
        else:
            self.show_all()
            self.present()
            self.visible = True
        return True

    # def setup_appindicator(self):
    #     self.ind = GahShomarIndicator(self, self.date)

    @log
    def set_icon_(self, *args):
        # day = khayyam.JalaliDate.today().day
        try:
            icon = Gtk.IconTheme.load_icon(
                Gtk.IconTheme(),
                'gahshomar',
                512, 0)
        except Exception:
            # logger.exception(Exception)
            icon = Gtk.IconTheme.load_icon(
                Gtk.IconTheme(),
                'persian-calendar',
                512, 0)
        self.set_icon(icon)