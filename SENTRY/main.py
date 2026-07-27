"""
SENTRY — Trading Operating System
Phase 2: Durable storage wired in.

What this file does:
1. Opens dashboard/boot.html inside a native desktop window. boot.html
   pulls saved data from SQLite (via the Api class below) into
   localStorage, then hands off to the real dashboard (index.html).
2. Exposes storage_get_all / storage_set_item / storage_remove_item to
   JavaScript — these are what dashboard/index.html's persistence patch
   (top of its <head>) and boot.html both call into.

See storage.py for the actual database logic, and PROJECT_MASTER.md
Section 3.1 for why this generic key-value approach was chosen for
Phase 2.
"""

import webview

import storage


class Api:
    """
    Anything added as a method here becomes callable from JavaScript as
    window.pywebview.api.<method_name>(...).
    """

    def hello(self):
        return "Hello from Python — bridge is working!"

    def storage_get_all(self):
        """Called once by boot.html on startup to hydrate localStorage."""
        return storage.get_all_items()

    def storage_set_item(self, key, value):
        """Called by the persistence patch every time the dashboard
        writes to localStorage — mirrors that write into SQLite."""
        storage.set_item(key, value)
        return True

    def storage_remove_item(self, key):
        storage.remove_item(key)
        return True


if __name__ == "__main__":
    # Make sure the database file/table exist before the window opens.
    storage.get_connection()

    api = Api()

    window = webview.create_window(
        title="SENTRY — Trading Operating System",
        url="dashboard/boot.html",
        js_api=api,
        width=1440,
        height=900,
        min_size=(1100, 700),
    )

    # debug=True opens a right-click "Inspect" option so you can see the
    # browser console (Console tab) if anything needs checking. Set this
    # to False once everything is stable.
    webview.start(debug=True)
