"""Local stand-in for the real-site scenarios. Not a public website."""

from __future__ import annotations

import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse


def _page(body: str) -> bytes:
    return (
        "<!doctype html><html><head><title>fixture</title></head><body>"
        + body
        + "</body></html>"
    ).encode()


_PAGES = {
    "/catalogue/page-1.html": _page(
        """
        <article class="product_pod">
          <h3><a href="book-a.html" title="Alpha Tale">Alpha Tale</a></h3>
          <p class="star-rating Four">Four</p>
          <p class="price_color">£30.00</p>
        </article>
        <article class="product_pod">
          <h3><a href="book-b.html" title="Beta Tale">Beta Tale</a></h3>
          <p class="star-rating Five">Five</p>
          <p class="price_color">£10.00</p>
        </article>
        <li class="next"><a href="page-2.html">next</a></li>
        """
    ),
    "/catalogue/page-2.html": _page(
        """
        <article class="product_pod">
          <h3><a href="book-c.html" title="Gamma Tale">Gamma Tale</a></h3>
          <p class="star-rating Four">Four</p>
          <p class="price_color">£12.50</p>
        </article>
        """
    ),
    "/catalogue/book-c.html": _page("<h1>Gamma Tale</h1><p class=\"price_color\">£12.50</p>"),
    "/wiki/Gamma_Tale": _page(
        "<p id=\"wiki-p\">Gamma Tale is a fixture novel by Mina Stone. "
        "The paragraph is long enough to count as a summary for the verifier and stays on this page.</p>"
    ),
    "/login": _page(
        """
        <form method="post" action="/inventory">
          <input id="user-name" name="user">
          <input id="password" name="password" type="password">
          <button id="login-button" type="submit">Login</button>
        </form>
        """
    ),
    "/inventory": _page(
        """
        <a id="add-to-cart-one" href="/inventory-1">Add</a>
        <a id="add-to-cart-two" href="/inventory-2">Add</a>
        """
    ),
    "/inventory-1": _page('<a id="add-to-cart-two" href="/inventory-2">Add</a>'),
    "/inventory-2": _page('<a class="shopping_cart_link" href="/cart">Cart</a>'),
    "/cart": _page('<a id="checkout" href="/checkout">Checkout</a>'),
    "/checkout": _page(
        """
        <form method="post" action="/overview">
          <input id="first-name" name="first">
          <input id="last-name" name="last">
          <input id="postal-code" name="postal">
          <button id="continue" type="submit">Continue</button>
        </form>
        """
    ),
    "/overview": _page('<div class="summary_total_label">Total: $39.98</div>'),
    "/hn": _page(
        """
        <span class="titleline"><a href="https://example.com/a">First headline about agents</a></span>
        <span class="titleline"><a href="https://example.com/b">Second headline about browsers</a></span>
        <span class="titleline"><a href="https://example.com/c">Third headline about repair</a></span>
        """
    ),
    "/arxiv": _page(
        """
        <li class="arxiv-result"><p class="title">Browser agents one</p><p class="authors">A Author</p></li>
        <li class="arxiv-result"><p class="title">Browser agents two</p><p class="authors">B Author</p></li>
        <li class="arxiv-result"><p class="title">Browser agents three</p><p class="authors">C Author</p></li>
        """
    ),
    "/dynamic": _page('<a id="start" href="/dynamic-done">Start</a>'),
    "/dynamic-done": _page("<h1>Hello World</h1>"),
    "/dropdown": _page(
        """
        <form method="post" action="/dropdown-done">
          <select id="dropdown" name="dropdown">
            <option value="1">Option 1</option>
            <option value="2">Option 2</option>
          </select>
          <button id="dropdown-go" type="submit">Go</button>
        </form>
        """
    ),
    "/upload": _page(
        """
        <form method="post" action="/upload-done">
          <input id="file-upload" type="file" name="file">
          <button id="file-submit" type="submit">Upload</button>
        </form>
        """
    ),
    "/recovery-broken": _page('<a href="/landed">Continue</a>'),
    "/landed": _page("<h1>landed</h1>"),
}


class _Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/wiki":
            body = _page('<a class="wiki-result" href="/wiki/Gamma_Tale">Gamma Tale</a>')
            return self._send(body)
        if path == "/dropdown-done":
            return self._send(_page("<p>Option 2 selected</p>"))
        body = _PAGES.get(path)
        if body is None:
            self.send_error(404)
            return
        self._send(body)

    def do_POST(self):
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length).decode()
        fields = parse_qs(raw)
        path = urlparse(self.path).path
        if path == "/dropdown-done":
            value = (fields.get("dropdown") or [""])[0]
            text = "Option 2 selected" if value == "2" else "not selected"
            return self._send(_page(f"<p>{text}</p>"))
        if path == "/upload-done":
            name = (fields.get("file") or [""])[0]
            return self._send(_page(f"<h1>File Uploaded</h1><p>{name}</p>"))
        body = _PAGES.get(path)
        if body is None:
            self.send_error(404)
            return
        self._send(body)

    def _send(self, body: bytes) -> None:
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *_args):
        return


def serve() -> tuple[ThreadingHTTPServer, str]:
    server = ThreadingHTTPServer(("127.0.0.1", 0), _Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, f"http://127.0.0.1:{server.server_address[1]}"
