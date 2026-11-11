#!/usr/local/bin/python
"""Fictional website for the NYITSec HTML-source investigation.

Only the HTTP response exposes the review clue. This file is excluded from
student working copies and made root-readable by .website-start.sh.
The server drops privileges before accepting requests.
"""

from http.server import BaseHTTPRequestHandler, HTTPServer
import os

HOST = "127.0.0.1"
PORT = 8765

PAGE = r"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="Visit the fictional Harborview Learning Center.">
  <title>Harborview Learning Center | Community Workshops</title>
  <style>
    :root { color-scheme: light; font-family: system-ui, -apple-system, sans-serif;
            background:#f4f7fb; color:#24334a; }
    * { box-sizing:border-box; }
    body { margin:0; line-height:1.6; }
    a { color:inherit; text-decoration:none; }
    header { background:#fff; border-bottom:1px solid #dbe5ed; padding:17px 7%; }
    .nav { display:flex; justify-content:space-between; align-items:center; gap:16px; flex-wrap:wrap; max-width:1120px; margin:auto; }
    .brand { color:#1b4979; font-weight:800; font-size:1.13rem; letter-spacing:-.025em; }
    nav { display:flex; gap:23px; font-size:.92rem; color:#56677c; }
    nav a:hover { color:#125b94; }
    .hero { background:linear-gradient(125deg,#11395f,#136c83); color:#fff; padding:74px 7% 79px; }
    .hero .inner { max-width:1120px; margin:auto; }
    .eyebrow { font-size:.75rem; text-transform:uppercase; letter-spacing:.2em; color:#b1e5e7; font-weight:750; }
    h1 { font-size:clamp(2.05rem,4.4vw,3.4rem); max-width:660px; line-height:1.14; margin:15px 0; letter-spacing:-.035em; }
    .subtitle { max-width:640px; color:#e1f4f6; font-size:1.05rem; }
    .pill { display:inline-block; margin-top:18px; padding:11px 19px; border-radius:25px; background:#fff; color:#14566c; font-weight:700; font-size:.9rem; }
    main { max-width:1120px; padding:50px 7% 70px; margin:auto; }
    .kicker { color:#247f85; text-transform:uppercase; font-size:.73rem; letter-spacing:.13em; font-weight:800; }
    h2 { font-size:1.75rem; letter-spacing:-.025em; margin:5px 0 8px; }
    .intro { color:#64778a; max-width:650px; margin:0 0 25px; }
    .cards { display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:17px; }
    .card { background:#fff; border:1px solid #e0e8ee; border-radius:14px; padding:23px; box-shadow:0 5px 18px #17395b0a; }
    .tag { background:#e1f3f0; color:#176a65; font-size:.72rem; border-radius:20px; padding:4px 10px; font-weight:700; display:inline-block; }
    h3 { margin:15px 0 5px; font-size:1.14rem; }
    .card p { font-size:.92rem; color:#62748a; margin:5px 0 15px; }
    .meta { font-size:.83rem; font-weight:700; color:#325c76; }
    .note { background:#e9f3f6; border-left:4px solid #2d8c91; border-radius:9px; padding:19px 23px; margin-top:29px; }
    footer { background:#112f4e; padding:24px 7%; text-align:center; color:#b8cbd9; font-size:.84rem; }
    @media(max-width:520px) { .hero{padding-top:55px;padding-bottom:55px;} nav{gap:12px;} }
  </style>
</head>
<body>
  <header>
    <div class="nav">
      <a class="brand" href="#top">◆ Harborview Learning Center</a>
      <nav aria-label="Main navigation">
        <a href="#workshops">Workshops</a>
        <a href="#hours">Visit Us</a>
        <a href="#about">About</a>
      </nav>
    </div>
  </header>
  <section class="hero" id="top">
    <div class="inner">
      <div class="eyebrow">Learning is for everyone</div>
      <h1>Explore something new in your community.</h1>
      <p class="subtitle">From creative technology to practical everyday skills, discover welcoming workshops for curious minds of all ages.</p>
      <a class="pill" href="#workshops">Explore workshops</a>
    </div>
  </section>
  <main>
    <section id="workshops">
      <div class="kicker">What's happening</div>
      <h2>Upcoming workshops</h2>
      <p class="intro">Small groups, friendly instructors, and plenty of room to ask questions. All sessions are part of this fictional training website.</p>
      <div class="cards">
        <article class="card"><span class="tag">Technology</span><h3>Computer Basics</h3><p>Learn file organization, useful shortcuts, and safe browsing habits.</p><div class="meta">Tuesday · 4:00 PM</div></article>
        <article class="card"><span class="tag">Creative</span><h3>Design Your Own Poster</h3><p>Try colors, shapes, and simple layouts in a hands-on design session.</p><div class="meta">Thursday · 3:30 PM</div></article>
        <article class="card"><span class="tag">Community</span><h3>Everyday Digital Safety</h3><p>Identify suspicious messages and protect your online accounts.</p><div class="meta">Saturday · 11:00 AM</div></article>
      </div>
    </section>
    <section class="note" id="hours">
      <strong>Visit us</strong><div>Open Monday–Saturday, 9 AM–6 PM.</div>
      <div>Location: Harborview Community Center (fictional).</div>
    </section>
    <section id="about" style="margin-top:34px">
      <h2>About the center</h2>
      <p class="intro">We believe learning is easier when everyone feels welcome to explore. This demonstration page does not collect visitor information or connect to a real organization.</p>
    </section>
  </main>
  <!--
    Internal publishing checklist. This note is not displayed by the browser.
    Training review code: NYITSEC-SOURCE-26
    Reminder: HTML source comments are public to anyone who inspects the page.
  -->
  <footer>© Harborview Learning Center · Fictional training website</footer>
</body>
</html>
"""


class SiteHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/favicon.ico":
            self.send_response(204)
            self.end_headers()
            return
        if self.path not in ("/", "/index.html"):
            self.send_error(404, "Page not found")
            return
        data = PAGE.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", "default-src 'none'; style-src 'unsafe-inline'")
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, format, *args):
        # No per-student access logs.
        pass


def main():
    server = HTTPServer((HOST, PORT), SiteHandler)
    if os.geteuid() == 0:
        # Root is only needed by .init to launch a protected source file.
        # HTTP handling runs without privileged permissions.
        os.setgroups([])
        os.setgid(1000)
        os.setuid(1000)
    server.serve_forever(poll_interval=0.2)


if __name__ == "__main__":
    main()
