"""
SENTRY — Trading Operating System
Phase 1: Skeleton desktop app.

What this file does:
1. Opens your existing TOS dashboard (dashboard/index.html) inside a
   native desktop window (no browser needed).
2. Proves Python <-> JavaScript communication works, by having the
   page ask Python for a message once the bridge is truly ready, and
   putting that message in the window's title bar.

Nothing in your dashboard's data/logic is wired up yet — that starts
in Phase 2. This phase only proves the shell works end to end.
"""

import webview


class Api:
    """
    Anything you add as a method here becomes callable from JavaScript
    as window.pywebview.api.<method_name>(...). This is the bridge
    every later phase (journal, broker data, analytics) will use.
    """

    def hello(self):
        return "Hello from Python — bridge is working!"


def on_loaded(window):
    """
    Runs once the dashboard HTML has loaded. The injected script below
    waits for pywebview's own 'pywebviewready' signal before calling
    the bridge — this avoids a race condition where the page finishes
    loading slightly before the Python bridge is actually attached.
    """
    window.evaluate_js(
        """
        (function() {
            function runBridgeTest() {
                window.pywebview.api.hello().then(function(result) {
                    document.title = "SENTRY — " + result;
                    console.log("[SENTRY bridge test]", result);
                });
            }
            if (window.pywebview && window.pywebview.api) {
                runBridgeTest();
            } else {
                window.addEventListener('pywebviewready', runBridgeTest);
            }
        })();
        """
    )


if __name__ == "__main__":
    api = Api()

    window = webview.create_window(
        title="SENTRY — Trading Operating System",
        url="dashboard/index.html",
        js_api=api,
        width=1440,
        height=900,
        min_size=(1100, 700),
    )

    window.events.loaded += on_loaded

    # debug=True opens a right-click "Inspect" option so you can see
    # the browser console (Console tab) and confirm the bridge test
    # message printed. Set this to False once everything is stable.
    webview.start(debug=True)
