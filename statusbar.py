from gi.repository import GObject, GLib

# this is just a temporary polyfill because Gedit.Statusbar.flash_message
# is not currently available

class Statusbar():
    def __init__(self, statusbar, ctx_name, flash_length=3):
        self.statusbar = statusbar
        self.context_id = statusbar.get_context_id(ctx_name)
        self.message_id = 0
        self.flash_timeout = 0
        self.flash_length = flash_length

    def flash_message(self, msg):
        if self.flash_timeout:
            GLib.source_remove(self.flash_timeout)
            self.statusbar.remove(self.context_id, self.message_id)

        self.message_id = self.statusbar.push(self.context_id, msg)
        self.flash_timeout = GLib.timeout_add_seconds(self.flash_length, self.remove_timeout)

    def remove_timeout(self):
        self.statusbar.remove(self.context_id, self.message_id)
        self.flash_timeout = 0
        return False


