import socket
import threading
import time

import webview

from app import app


HOST = "127.0.0.1"
PORT = 5000
APP_URL = f"http://{HOST}:{PORT}"


def run_flask():

    app.run(
        host=HOST,
        port=PORT,
        debug=False,
        use_reloader=False
    )


def wait_for_server(
    host=HOST,
    port=PORT,
    timeout=20
):

    start_time = time.time()

    while time.time() - start_time < timeout:

        try:

            with socket.create_connection(
                (host, port),
                timeout=1
            ):
                return True

        except OSError:

            time.sleep(0.2)

    return False


def start_app():

    flask_thread = threading.Thread(
        target=run_flask,
        daemon=True
    )

    flask_thread.start()

    server_ready = wait_for_server()

    if not server_ready:

        raise RuntimeError(
            "Flask server could not start."
        )

    webview.create_window(
        title="Hostel Leave Management System",
        url=APP_URL,
        width=1280,
        height=800,
        min_size=(1000, 650),
        resizable=True
    )

    webview.start()


if __name__ == "__main__":

    start_app()