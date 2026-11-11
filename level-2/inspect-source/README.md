# Officer notes: Inspect the Source

**Module:** \`level-2\` | **ID:** \`inspect-source\` | **Difficulty:** Easy

## Purpose

Students learn that a website can expose information through its **HTML source**, including comments that are not rendered in the visible page. This is a fictional, isolated web-service exercise, not an exercise involving a public website.

The browser-visible site is a polished fictional Harborview Learning Center landing page. An internal QA comment contains the synthetic answer code; the student sees it only when inspecting the HTML source, not in the rendered page. The protected checker stores a SHA-256 digest and reveals pwn.college's per-student \`/flag\` after an exact match.

## Challenge startup

- Standard \`.init\` staging and Bash startup remain **byte-for-byte identical to the shared template**, except for an approved, validated two-line extension to call \`/challenge/.website-start.sh\`.
- \`.website-start.sh\` locks down \`/challenge/.website.py\` to mode \`0600\`, launches a local Python HTTP server in the background, and waits until an HTTP health check passes. This protects the source file from ordinary filesystem inspection while leaving the public HTML accessible through HTTP.
- \`.website.py\` binds only to **127.0.0.1:8765**, serves **GET / or /index.html** and a 204 favicon, has no uploads or dynamic parameters, sets basic security headers, and **drops to the \`hacker\` UID after binding**. The HTML is generated in memory; no \`.html\` file is copied into the student workspace.
- \`.ctfignore\` explicitly excludes the server implementation and its startup script from \`/nyitsec-ctf\`.
- The student's \`/nyitsec-ctf\` starts empty for this challenge. Their intended investigation path is **Workspace → Desktop → Firefox → http://127.0.0.1:8765/**.

**Important limitation:** No ordinary web server can guarantee that only Firefox can inspect HTTP source; a student could also use \`curl\` or another HTTP client. The exercise makes the browser the expected learning workflow, without fragile user-agent filters or artificial access restrictions.

## Live smoke tests

1. Launch the challenge and check \`pwd\` shows \`/nyitsec-ctf\`, with no website implementation files staged.
2. Open Workspace → Desktop → Firefox and load **http://127.0.0.1:8765/**. Confirm the fictional page renders without errors or external content.
3. Use **View Page Source** or **Ctrl+U**. Confirm the internal publishing comment contains the review code.
4. Verify \`ls -la /nyitsec-ctf\` has no \`.website.py\` and \`cat /challenge/.website.py\` reports permission denied.
5. Confirm \`nyitsec-answer\` rejects incorrect input and accepts the exact code from the HTML source, revealing the unique platform flag.
6. Verify old Fundamentals and Level 2 exercises remain unchanged.

The root-owned initialization script's web-service suffix is checked by the repository validator, and the Python unit tests exercise HTTP serving, HTML source, permissions conventions, workspace copy exclusions, and answer validation.
