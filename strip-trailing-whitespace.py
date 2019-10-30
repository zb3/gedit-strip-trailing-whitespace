# -*- coding: utf8 -*-

from gi.repository import GObject, Gio, Gtk, Gedit

from statusbar import Statusbar

class StripWSAppActivatable(GObject.Object, Gedit.AppActivatable):
    app = GObject.Property(type=Gedit.App)

    def __init__(self):
        GObject.Object.__init__(self)

    def do_activate(self):
        self.app.add_accelerator("<Primary><Shift>R", "win.striptrailingwhitespace", None)

    def do_deactivate(self):
        self.app.remove_accelerator("win.striptrailingwhitespace", None)


class StripWSWindowActivatable(GObject.Object, Gedit.WindowActivatable):
    window = GObject.Property(type=Gedit.Window)

    def __init__(self):
        GObject.Object.__init__(self)

    def do_activate(self):
        action = Gio.SimpleAction(name="striptrailingwhitespace")
        action.connect('activate', lambda a, p: self.strip_trailing_ws())
        self.window.add_action(action)

        self.statusbar = Statusbar(self.window.get_statusbar(), 'strip_ws')

    def do_deactivate(self):
        self.window.remove_action("striptrailingwhitespace")

    def do_update_state(self):
        view = self.window.get_active_view()
        enable = view is not None and view.get_editable()
        self.window.lookup_action("striptrailingwhitespace").set_enabled(enable)

    def strip_trailing_ws(self):
        view = self.window.get_active_view()
        if view and hasattr(view, "strip_ws_view_activatable"):
            lines_modified = view.strip_ws_view_activatable.strip_trailing_ws()

            if lines_modified:
                message = "Stripped trailing whitespace from %d lines" % lines_modified
            else:
                message = "No trailing whitespace present"

            self.statusbar.flash_message(message)


class StripWSViewActivatable(GObject.Object, Gedit.ViewActivatable):
    view = GObject.Property(type=Gedit.View)

    def __init__(self):
        GObject.Object.__init__(self)

    def do_activate(self):
        self.view.strip_ws_view_activatable = self

    def do_deactivate(self):
        delattr(self.view, "strip_ws_view_activatable")

    def strip_trailing_ws(self):
        buff = self.view.get_buffer()
        if buff is None:
            return

        if buff.get_has_selection():
            cur, end = buff.get_selection_bounds()
        else:
            cur, end = buff.get_bounds()

        space_start = cur.copy()
        trailing_whitespace = False

        char_count = end.get_offset() - cur.get_offset()
        lines_modified = 0

        buff.begin_user_action()

        for _ in range(char_count):
            ch = cur.get_char()

            if ch in ('\r', '\n'):
                if trailing_whitespace:
                    buff.delete(space_start, cur)
                    trailing_whitespace = False
                    lines_modified += 1

            elif ch in (' ', '\t'):
                if not trailing_whitespace:
                    trailing_whitespace = True
                    space_start.assign(cur)

            else:
                trailing_whitespace = False

            cur.forward_char()

        buff.end_user_action()

        return lines_modified


