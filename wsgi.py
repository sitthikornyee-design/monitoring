from __future__ import annotations

import os

from app import app


def main() -> None:
    from waitress import serve

    host = os.getenv("WSGI_HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8080"))
    threads = int(os.getenv("WAITRESS_THREADS", "4"))

    serve(app, host=host, port=port, threads=threads)


if __name__ == "__main__":
    main()
