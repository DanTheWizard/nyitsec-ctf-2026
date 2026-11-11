#!/usr/local/bin/python
"""INTENTIONALLY VULNERABLE NYITSec CTF forum (fictional, localhost only).

For NYITSec / ITS review see docs/its-review/broken-login/README.md.
DO NOT reuse these SQL queries or this application for a real website.
"""

from contextlib import closing
from html import escape
from http import HTTPStatus
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Lock
from urllib.parse import parse_qs, urlsplit
import os
import pwd
import secrets
import sqlite3

HOST = "127.0.0.1"
PORT = 80
DOMAIN = "nyitsecwebsite.test"
DB_PATH = Path("/run/nyitsec-forum/forum.sqlite3")
NUKE_PASSWORD = "OrbitingToaster#73"

# Absolutely everything here is synthetic challenge data.
PEOPLE = (
    ("admin", "CopperGate!26", "admin"),
    ("packetpanda", "glowworm-lab-26", "member"),
    ("rootbeer", "rootbeer-is-not-root", "member"),
    ("hexkitten", "debug-the-cat", "member"),
    ("bitwizard", "wizards-love-bits", "member"),
)
POSTS = (
    ("Introductions", "Welcome to the NYITSec Underground!", "admin",
     "Welcome to the fictional forum. Tell us your favorite technology and remember to keep the conversation respectful."),
    ("Hardware Lab", "Found a mysterious UART header", "bitwizard",
     "I found a serial header on an old board. Thinking about using a USB adapter and a logic analyzer before powering anything."),
    ("CTF Talk", "What's your favorite decoding trick?", "hexkitten",
     "I keep a notes file with Base64, ROT13, and hex recipes. The trick is recognizing what you are actually looking at."),
    ("Off Topic", "The Great Keyboard Switch Debate", "rootbeer",
     "Tactile or linear switches? We need a scientific study involving a blindfold and a very loud keyboard."),
    ("Network Corner", "DNS has more than A records", "packetpanda",
     "A neat lab showed me how MX, TXT, and CNAME records can tell a surprisingly long story."),
    ("Show and Tell", "My Raspberry Pi status display", "bitwizard",
     "Built a tiny dashboard with temperature, uptime, and a pixel-art wizard. Next step is making it less cursed."),
    ("Off Topic", "Best snack for a midnight debugging session", "hexkitten",
     "I vote for chocolate chip cookies and cold water. No more soda on the electronics bench."),
    ("CTF Talk", "Hint etiquette during competitions", "admin",
     "Try to teach the idea, not simply paste an answer. A good hint points toward the next question."),
    ("Hardware Lab", "Oscilloscope troubleshooting tips", "packetpanda",
     "Before blaming the circuit, check your ground clip, probe attenuation, and channel coupling."),
    ("Announcements", "Forum signup queue is now open", "admin",
     "This super secure forum has a limited beta. New accounts must join the waiting list first."),
    ("Network Corner", "Packet captures versus browser developer tools", "rootbeer",
     "Both can help reveal what a client is sending, but there is no substitute for understanding the protocol."),
    ("Show and Tell", "Favorite terminal color themes?", "bitwizard",
     "Dark navy and cyan, obviously. Bonus points if it looks like a spaceship control panel."),
)
WAITLIST = (
    "aspiring-coder@example.test",
    "curious-hacker@example.test",
    "study-buddy@example.test",
    "night-shift@example.test",
    "new-member@example.test",
)

STYLES = """
:root{color-scheme:dark;--bg:#0b1122;--panel:#141e33;--edge:#2b3b58;
--ink:#eef5ff;--sub:#a0b2ce;--cyan:#69e3e6;--lime:#a8f596;--warn:#ffc47d;
font-family:system-ui,-apple-system,Segoe UI,Arial,sans-serif}
*{box-sizing:border-box}body{margin:0;background:radial-gradient(ellipse at 10% -10%,#193457,#0b1122 58%);
color:var(--ink);line-height:1.58;min-height:100vh}
a{color:var(--cyan);text-decoration:none}a:hover{text-decoration:underline}
nav{padding:16px max(24px,calc((100% - 1120px)/2));background:#0e1729eb;
border-bottom:1px solid var(--edge);display:flex;align-items:center;gap:16px;flex-wrap:wrap}
.brand{font-weight:900;letter-spacing:.09em;color:white;font-size:1.15rem}
.brand span{color:var(--cyan)}.spacer{flex:1}.navlink{color:#c9d8ed;font-size:.9rem}
button,.btn{display:inline-block;border:0;border-radius:10px;cursor:pointer;background:var(--cyan);
color:#102237;font-weight:750;padding:11px 17px;font:inherit}
button:hover,.btn:hover{filter:brightness(1.1);text-decoration:none}
.btn.alt{background:#283a54;color:#ecf4ff}.btn.danger{background:#f47b91;color:#1d0c14}
main{max-width:1120px;margin:0 auto;padding:35px 24px 80px}
.eyebrow{text-transform:uppercase;letter-spacing:.15em;font-size:.73rem;color:var(--cyan);font-weight:850}
h1{font-size:clamp(2rem,4vw,3.4rem);line-height:1.1;letter-spacing:-.035em;margin:12px 0}
h2{font-size:1.45rem;margin:0 0 15px;letter-spacing:-.02em}h3{font-size:1.04rem;margin:0 0 7px}
p{margin:8px 0 15px}.lead{color:#c8d8ed;max-width:680px;font-size:1.05rem}
.hero{padding:23px 0 37px}.pill{display:inline-block;padding:6px 10px;border:1px solid #5fae9d;
background:#1a3c3d;color:#baf4d8;border-radius:99px;font-size:.75rem;font-weight:850}
.grid{display:grid;grid-template-columns:minmax(0,1fr) 290px;gap:20px}
.panel{background:var(--panel);border:1px solid var(--edge);border-radius:14px;
padding:23px;box-shadow:0 14px 35px #030a1866}
.panel+.panel{margin-top:16px}.post{padding:19px 0;border-top:1px solid var(--edge)}
.post:first-of-type{border-top:0}.meta{font-size:.82rem;color:var(--sub)}
.category{display:inline-block;font-size:.74rem;font-weight:850;color:var(--lime);
text-transform:uppercase;letter-spacing:.055em}
.label{display:block;font-size:.87rem;font-weight:700;color:#d2e2f2;margin-bottom:7px}
input{display:block;width:100%;background:#0b1427;color:var(--ink);border:1px solid #47607d;
border-radius:9px;font:inherit;padding:12px 13px;margin-bottom:16px}
input:focus{outline:2px solid var(--cyan)}form{margin:0}.formbox{max-width:540px}
.notice{border-left:4px solid #6bbec1;background:#123140;border-radius:10px;
padding:14px 17px;color:#d8fbff;margin:13px 0 23px}
.notice.warn{background:#392a24;border-left-color:var(--warn);color:#ffe2b0}
.notice.danger{background:#431b2c;border-left-color:#ff91a7;color:#ffe0e8}
small{color:var(--sub)}.control{display:flex;gap:12px;flex-wrap:wrap;align-items:center}
.badge{background:#223f50;color:#a9faff;padding:5px 10px;border-radius:6px;font-size:.75rem;font-weight:800}
footer{border-top:1px solid var(--edge);color:#8298b4;text-align:center;padding:24px;font-size:.81rem}
.secret{padding:24px;background:#0d2d2c;border:1px solid #2a9e89;border-radius:13px;margin:20px 0}
.secret code{color:#baf9de;word-break:break-all;font-size:1.12rem}
@media(max-width:760px){.grid{grid-template-columns:1fr}nav{padding:14px 18px}main{padding:24px 16px 65px}}
"""


def seed_database(path: Path) -> None:
    """Create the fictional data once per disposable challenge container."""
    path = Path(path)
    if path.exists():
        return
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    with closing(sqlite3.connect(path)) as db:
        db.executescript("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                role TEXT NOT NULL
            );
            CREATE TABLE posts (
                id INTEGER PRIMARY KEY,
                category TEXT NOT NULL,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                body TEXT NOT NULL
            );
            CREATE TABLE signup_queue (
                id INTEGER PRIMARY KEY,
                email TEXT NOT NULL,
                joined_at TEXT NOT NULL
            );
            CREATE TABLE settings (name TEXT PRIMARY KEY, value TEXT NOT NULL);
            INSERT INTO settings (name, value) VALUES ('status', 'active');
        """)
        db.executemany(
            "INSERT INTO users(username,password,role) VALUES (?,?,?)", PEOPLE
        )
        db.executemany(
            "INSERT INTO posts(category,title,author,body) VALUES (?,?,?,?)", POSTS
        )
        db.executemany(
            "INSERT INTO signup_queue(email,joined_at) VALUES (?, '2026-11-11')",
            [(email,) for email in WAITLIST],
        )
        db.commit()


def table_exists(db: sqlite3.Connection, table: str) -> bool:
    return db.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (table,)
    ).fetchone() is not None


def is_nuked(db: sqlite3.Connection) -> bool:
    row = db.execute(
        "SELECT value FROM settings WHERE name='status'"
    ).fetchone()
    return bool(row and row[0] == "nuked")


def query_login(db: sqlite3.Connection, username: str, password: str):
    # DELIBERATE SQL INJECTION LESSON: string interpolation into a query.
    # In production these MUST be parameterized (see ITS review notes).
    query = (
        "SELECT username,role FROM users WHERE username = '"
        + username + "' AND password = '" + password + "' LIMIT 1"
    )
    return db.execute(query).fetchone()


def queue_registration(db: sqlite3.Connection, email: str) -> None:
    # DELIBERATE MULTI-STATEMENT SQL INJECTION LESSON.
    # sqlite3.executescript supports stacked statements, including DROP TABLE.
    script = (
        "INSERT INTO signup_queue(email,joined_at) VALUES ('"
        + email + "', '2026-11-11');"
    )
    db.executescript(script)


def search_posts(db: sqlite3.Connection, term: str):
    # Third, optional SQLi route: UNION-based data retrieval.
    sql = (
        "SELECT title,body FROM posts WHERE title LIKE '%"
        + term + "%' LIMIT 30"
    )
    return db.execute(sql).fetchall()


def render_page(title: str, body: str, session=None, banner="") -> bytes:
    account = session[0] if session else None
    role = session[1] if session else None
    nav = [
        '<a class="navlink" href="/">Forum</a>',
        '<a class="navlink" href="/search">Search</a>',
        '<a class="navlink" href="/queue">Join waitlist</a>',
    ]
    if role == "admin":
        nav.append('<a class="btn danger" href="/admin/nuke">☢ Nuke Forum</a>')
    if account:
        nav.append('<span class="badge">Signed in: ' + escape(account) + '</span>')
        nav.append('<form action="/logout" method="post"><button class="btn alt">Log out</button></form>')
    else:
        nav.append('<a class="btn alt" href="/login">Log in</a>')
    document = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{escape(title)} | NYITSec Underground</title>
<style>{STYLES}</style></head><body>
<nav><a class="brand" href="/">NYIT<span>SEC</span> // UNDERGROUND</a>
<div class="spacer"></div>{''.join(nav)}</nav>
<main>{banner}{body}</main>
<footer>NYITSec Underground • Fictional, isolated CTF demonstration • No real NYIT services or accounts</footer>
</body></html>"""
    return document.encode("utf-8")


def block(content: str, kind="") -> str:
    return '<div class="notice ' + escape(kind) + '">' + content + '</div>'


class ForumHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.0"

    def log_message(self, *_args):
        # Student traffic, emails, submitted credentials, and injections
        # must not be written to any web-server request log.
        pass

    def db(self):
        return sqlite3.connect(self.server.db_path, timeout=3)

    def session_info(self):
        header = self.headers.get("Cookie", "")
        cookie = SimpleCookie()
        try:
            cookie.load(header)
        except Exception:
            return (None, None)
        if "nyitsec_lab" not in cookie:
            return (None, None)
        token = cookie["nyitsec_lab"].value
        with self.server.lock:
            identity = self.server.sessions.get(token)
        return (token, identity)

    def respond(self, html: bytes, code=200, cookie=None):
        self.send_response(code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(html)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header(
            "Content-Security-Policy",
            "default-src 'none'; style-src 'unsafe-inline'; form-action 'self'",
        )
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("X-Frame-Options", "DENY")
        if cookie:
            self.send_header("Set-Cookie", cookie)
        self.end_headers()
        self.wfile.write(html)

    def show(self, title, html, code=200, cookie=None, alert=""):
        _, identity = self.session_info()
        self.respond(
            render_page(title, html, identity, alert), code=code, cookie=cookie
        )

    def fields(self):
        try:
            size = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            return None
        if size < 0 or size > 4096:
            return None
        raw = self.rfile.read(size).decode("utf-8", errors="replace")
        return {k: values[0] for k, values in parse_qs(
            raw, keep_blank_values=True, max_num_fields=15
        ).items()}

    def bad(self, message="The request could not be processed.", code=400):
        self.show("Request error", block(escape(message), "warn"), code=code)

    def allowed_host(self):
        # Deny use as a DNS-rebinding target. Health checks use localhost IP.
        header = self.headers.get("Host", "").lower()
        return header in {
            DOMAIN, f"{DOMAIN}:{self.server.server_port}",
            "127.0.0.1", f"127.0.0.1:{self.server.server_port}",
            "localhost", f"localhost:{self.server.server_port}",
        }

    def do_GET(self):
        if not self.allowed_host():
            self.bad("Unknown local hostname.", 421)
            return
        path = urlsplit(self.path).path
        if path == "/favicon.ico":
            self.send_response(204)
            self.end_headers()
            return
        if path == "/":
            self.home()
        elif path == "/login":
            self.login_form()
        elif path == "/queue":
            self.queue_form()
        elif path == "/search":
            params = parse_qs(urlsplit(self.path).query)
            self.search(params.get("q", [""])[0])
        elif path == "/thread":
            params = parse_qs(urlsplit(self.path).query)
            self.thread_page(params.get("id", ["0"])[0])
        elif path == "/admin/nuke":
            self.nuke_confirm()
        else:
            self.bad("Page not found.", 404)

    def do_POST(self):
        if not self.allowed_host():
            self.bad("Unknown local hostname.", 421)
            return
        form = self.fields()
        if form is None:
            self.bad("Invalid form submission.")
            return
        path = urlsplit(self.path).path
        if path == "/login":
            self.login(form)
        elif path == "/queue":
            self.queue(form)
        elif path == "/logout":
            self.logout()
        elif path == "/admin/nuke":
            self.nuke(form)
        else:
            self.bad("Unknown form action.", 404)

    def home(self):
        with closing(self.db()) as db:
            rows = db.execute(
                "SELECT id,category,title,author,body FROM posts "
                "ORDER BY id DESC LIMIT 20"
            ).fetchall()
            nuked = is_nuked(db)
            queue_up = table_exists(db, "signup_queue")
            waiting = (
                db.execute("SELECT COUNT(*) FROM signup_queue").fetchone()[0]
                if queue_up else 0
            )
        hero = (
            '<div class="hero"><div class="eyebrow">NYITSEC COMMUNITY FORUM · BETA</div>'
            '<h1>Welcome to the Underground.</h1>'
            '<p class="lead">Talk hardware, security labs, CTFs, and everything '
            'in between. A tiny home for curious minds and very questionable jokes.</p>'
            '<span class="pill">🔒 SUPER SECURE™ AUTHENTICATION SYSTEM</span></div>'
        )
        if nuked:
            hero += block(
                "<strong>Simulation complete.</strong> The fictional forum posts "
                "have been wiped. Reset this challenge to restore the test site.",
                "danger",
            )
        posts = ''.join(
            f'<div class="post"><div class="category">{escape(category)}</div>'
            f'<h3><a href="/thread?id={pid}">{escape(title)}</a></h3>'
            f'<div class="meta">by @{escape(author)} · Fictional community post</div>'
            f'<p>{escape(body[:155])}</p></div>'
            for pid, category, title, author, body in rows
        )
        if not posts:
            posts = '<p class="meta">No posts available.</p>'
        sidebar = (
            '<div class="panel"><h3>Community dashboard</h3>'
            f'<p class="meta">Threads: {len(rows)} · Waitlist: '
            f'{"offline" if not queue_up else str(waiting) + " waiting"}</p>'
            '<hr style="border:0;border-top:1px solid #2b3b58;margin:20px 0">'
            '<h3>Forum rules</h3>'
            '<p class="meta">Be curious. Stay respectful. Keep tests on authorized '
            'systems. Never trust a badge that says SUPER SECURE.</p>'
            '<a class="btn alt" href="/queue">Join the signup queue</a></div>'
        )
        self.show(
            "Forum",
            hero + '<div class="grid"><section class="panel"><h2>Latest threads</h2>'
            + posts + '</section><aside>' + sidebar + '</aside></div>',
        )

    def login_form(self, alert=""):
        body = (
            '<div class="hero"><div class="eyebrow">Member access</div>'
            '<h1>Sign in to the Underground.</h1>'
            '<p class="lead">For members who already have an account.</p></div>'
            '<section class="panel formbox"><h2>Member login</h2>'
            '<form method="post" action="/login">'
            '<label class="label" for="username">Username</label>'
            '<input required id="username" name="username" autocomplete="off" maxlength="512">'
            '<label class="label" for="password">Password</label>'
            '<input required type="password" id="password" name="password" maxlength="512">'
            '<button type="submit">Sign in</button></form>'
            '<p class="meta">NYITSec Underground · Super Secure™ login gateway</p>'
            '</section>'
        )
        self.show("Login", body, alert=alert)

    def login(self, form):
        username = form.get("username", "")[:512]
        password = form.get("password", "")[:512]
        try:
            with closing(self.db()) as db:
                identity = query_login(db, username, password)
        except sqlite3.Error:
            identity = None
        if not identity:
            self.login_form(block("Login failed. Please check your credentials.", "warn"))
            return
        token = secrets.token_urlsafe(32)
        with self.server.lock:
            self.server.sessions[token] = identity
        self.respond(
            render_page(
                "Logged in",
                '<section class="panel"><h2>Welcome, '
                + escape(identity[0]) + '!</h2><p>Login complete.</p>'
                '<a class="btn" href="/">Visit forum</a></section>',
                identity,
            ),
            cookie="nyitsec_lab=" + token + "; HttpOnly; SameSite=Strict; Path=/",
        )

    def logout(self):
        token, _ = self.session_info()
        with self.server.lock:
            self.server.sessions.pop(token, None)
            self.server.confirmations.pop(token, None)
        self.respond(
            render_page(
                "Signed out",
                '<section class="panel"><h2>Logged out.</h2>'
                '<a class="btn" href="/">Return to forum</a></section>',
            ),
            cookie="nyitsec_lab=; HttpOnly; SameSite=Strict; Max-Age=0; Path=/",
        )

    def queue_form(self, alert=""):
        body = (
            '<div class="hero"><div class="eyebrow">Membership beta</div>'
            '<h1>Get in line.</h1><p class="lead">We are gradually opening '
            'registration. Leave an address for a fictional invitation.</p></div>'
            '<section class="panel formbox"><h2>Signup waiting list</h2>'
            '<form action="/queue" method="post">'
            '<label class="label" for="email">Email address</label>'
            '<input id="email" name="email" type="text" required maxlength="1024" '
            'placeholder="you@example.test">'
            '<button type="submit">Request invite</button>'
            '</form><p class="meta">Demo only. No email will be sent.</p></section>'
        )
        self.show("Signup queue", body, alert=alert)

    def queue(self, form):
        email = form.get("email", "")[:1024]
        if not email:
            self.queue_form(block("Please enter an email address.", "warn"))
            return
        try:
            with closing(self.db()) as db:
                queue_registration(db, email)
        except sqlite3.Error:
            self.queue_form(block("The signup queue is unavailable. The forum database might need repair.", "warn"))
            return
        self.queue_form(block("Added to the fictional waiting list. Thanks!"))

    def search(self, term):
        term = term[:1024]
        results = []
        err = ""
        if term:
            try:
                with closing(self.db()) as db:
                    results = search_posts(db, term)
            except sqlite3.Error:
                err = block("Search failed. The query could not be processed.", "warn")
        html = (
            '<div class="hero"><div class="eyebrow">Community search</div>'
            '<h1>Find a discussion.</h1></div>'
            '<section class="panel"><form method="get" action="/search">'
            '<label class="label" for="q">Search posts</label>'
            '<input id="q" name="q" value="' + escape(term, quote=True)
            + '" placeholder="try keyboard, DNS, or CTF">'
            '<button>Search</button></form>' + err
        )
        for title, body in results:
            html += (
                '<div class="post"><h3>' + escape(str(title))
                + '</h3><p>' + escape(str(body)) + '</p></div>'
            )
        if term and not results:
            html += '<p class="meta">No matching threads.</p>'
        self.show("Search", html + "</section>")

    def thread_page(self, identifier):
        try:
            num = int(identifier)
        except ValueError:
            self.bad("Invalid thread ID.")
            return
        with closing(self.db()) as db:
            row = db.execute(
                "SELECT category,title,author,body FROM posts WHERE id=?", (num,)
            ).fetchone()
        if not row:
            self.bad("Thread not found.", 404)
            return
        category, title, author, body = row
        self.show(
            str(title),
            '<section class="panel"><span class="category">' + escape(category)
            + '</span><h1>' + escape(title) + '</h1><div class="meta">by @'
            + escape(author) + '</div><p>' + escape(body) + '</p>'
            '<hr style="border:0;border-top:1px solid #2b3b58">'
            '<p class="meta">Replies are disabled during this fictional beta.</p>'
            '<a href="/">Back to threads</a></section>',
        )

    def require_admin(self):
        token, identity = self.session_info()
        if not identity or identity[1] != "admin":
            self.show(
                "Restricted",
                block("Administrator access required.", "danger")
                + '<a class="btn alt" href="/login">Sign in</a>',
                code=403,
            )
            return None
        return token

    def nuke_confirm(self):
        token = self.require_admin()
        if token is None:
            return
        nonce = secrets.token_urlsafe(24)
        with self.server.lock:
            self.server.confirmations[token] = nonce
        body = (
            '<div class="hero"><div class="eyebrow">Administrative control panel</div>'
            '<h1>☢ Nuke the forum?</h1>'
            '<p class="lead">This will wipe only disposable, fictional '
            'forum posts inside this challenge container.</p></div>'
            + block(
                "<strong>Are you absolutely sure?</strong> This is a simulation. "
                "A challenge reset restores the original forum.",
                "danger",
            )
            + '<section class="panel formbox"><h2>Confirm simulated deletion</h2>'
            '<form action="/admin/nuke" method="post">'
            '<input type="hidden" name="confirm" value="' + nonce + '">'
            '<button class="btn danger" type="submit">Yes, nuke this fictional forum</button>'
            '</form><p><a href="/">Cancel and return to forum</a></p></section>'
        )
        self.show("Nuke confirmation", body)

    def nuke(self, form):
        token = self.require_admin()
        if token is None:
            return
        nonce = form.get("confirm", "")
        with self.server.lock:
            expected = self.server.confirmations.pop(token, None)
        if not expected or not secrets.compare_digest(nonce, expected):
            self.bad("The confirmation has expired. Open the control panel again.", 403)
            return
        with closing(self.db()) as db:
            if table_exists(db, "signup_queue"):
                self.show(
                    "Safety interlock",
                    block(
                        "Nuke interlock active: the signup waiting queue still "
                        "exists. Clear the queue before this simulation can run.",
                        "warn",
                    ) + '<a class="btn alt" href="/">Return to forum</a>',
                )
                return
            if not is_nuked(db):
                with db:
                    db.execute("DELETE FROM posts")
                    db.execute(
                        "UPDATE settings SET value='nuked' WHERE name='status'"
                    )
        self.show(
            "Simulated nuke complete",
            '<div class="hero"><div class="eyebrow">Simulation completed</div>'
            '<h1>Forum successfully nuked.</h1>'
            '<p class="lead">Only fictional test posts were removed. No '
            'real systems or accounts were affected.</p></div>'
            + '<div class="secret"><h2>Nuke authorization password</h2><code>'
            + escape(NUKE_PASSWORD) + '</code><p>Enter this exact password '
            'using <strong>nyitsec-answer</strong> in the challenge terminal.</p>'
            '</div><a class="btn alt" href="/">Return to forum</a>',
        )


class ForumServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True

    def __init__(self, address, db_path):
        super().__init__(address, ForumHandler)
        self.db_path = Path(db_path)
        self.sessions = {}
        self.confirmations = {}
        self.lock = Lock()


def create_server(host=HOST, port=PORT, db_path=DB_PATH):
    return ForumServer((host, port), db_path)


def main():
    account = pwd.getpwnam("nobody")
    DB_PATH.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    os.chown(DB_PATH.parent, account.pw_uid, account.pw_gid)
    os.chmod(DB_PATH.parent, 0o700)
    seed_database(DB_PATH)
    os.chown(DB_PATH, account.pw_uid, account.pw_gid)
    os.chmod(DB_PATH, 0o600)

    server = create_server()
    if os.geteuid() == 0:
        os.setgroups([])
        os.setgid(account.pw_gid)
        os.setuid(account.pw_uid)
    server.serve_forever(poll_interval=0.2)


if __name__ == "__main__":
    main()
