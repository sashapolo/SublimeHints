"""
Auxillary stub module for developing plugins outside of the real Sublime Text environment.

See API official reference at http://www.sublimetext.com/docs/2/api_reference.html
"""

def set_timeout(callback, delay):
    """
    Calls the given callback after the given delay (in milliseconds).
    Callbacks with an equal delay will be run in the order they were added.
    It is safe to call setTimeout from multiple threads.
    """
    pass

def status_message(string):
    """ Sets the message that appears in the status bar."""
    pass

def error_message(string):
    """Displays an error dialog to the user."""
    pass

def message_dialog(string):
    """Displays a message dialog to the user."""
    pass

def ok_cancel_dialog(string, ok_button=None):
    """
    Displays an ok / cancel question dialog to the user.
    If ok_button is provided, this may be used as the text on the ok button.
    Returns True if the user presses the ok button.
    """
    pass

def load_settings(base_name):
    """
    Loads the named settings. The name should include a file name and extension,
    but not a path. The packages will be searched for files matching the
    base name, and the results will be collated into the settings object.
    Subsequent calls to load_settings with the name base_name will return
    the same object, and not load the settings from disk again.
    """
    pass

def save_settings(base_name):
    """Flushes any in-memory changes to the named settings object to disk."""
    pass

def windows():
    """Returns a list of all the open windows."""
    pass

def active_window():
    """Returns the most recently used window."""
    pass

def packages_path():
    """Returns the base path to the packages."""
    pass

def installed_packages_path():
    """Returns the path where all the user's *.sublime-package files are."""
    pass

def get_clipboard():
    """Returns the contents of the clipboard."""
    pass

def set_clipboard(string):
    """Sets the contents of the clipboard."""
    pass

def score_selector(scope, selector):
    """
    Matches the selector against the given scope, returning a score.
    A score of 0 means no match, above 0 means a match.
    Different selectors may be compared against the same scope:
    a higher score means the selector is a better match for the scope.
    """
    pass

def run_command(string, args=None):
    """Runs the named ApplicationCommand with the (optional) given arguments."""
    pass

def log_commands(flag):
    """
    Controls command logging. If enabled, all commands run from key bindings
    and the menu will be logged to the console.
    """
    pass

def log_input(flag):
    """
    Controls input logging. If enabled, all key presses will be logged to the console.
    """
    pass

def version():
    """Returns the version number"""
    pass

def platform():
    """Returns the platform, which may be "osx", "linux" or "windows."""
    pass

def arch():
    """ Returns the CPU architecture, which may be "x32" or "x64"."""
    pass

# Following functions have not documented.
# TODO: investigate what they do actually
def channel(): pass
def get_macro(): pass
def log_result_regex(): pass
def score_selector(): pass


class Edit: pass
class Region: pass
class RegionSet: pass
class Settings: pass
class View: pass
class Window: pass
