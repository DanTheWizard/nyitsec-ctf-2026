# Inspect the Source

A fictional community website looks completely normal, but an investigator suspects that something was left behind in its **HTML source**.

**Goal:** Find the hidden review code without relying on anything shown on the visible webpage.

### Open the website

1. Start the challenge and select **Workspace → Desktop**.
2. Open **Firefox** inside the Desktop.
3. Visit **http://harborview.test/**.

The fictional `.test` domain points to **127.0.0.1 inside this challenge VM only**. It is not a public website and cannot be accessed from your own computer.

### Investigate

The page may look ordinary, but webpages contain more than what appears on screen. In Firefox, try **right-click → View Page Source** or press **Ctrl+U**.

Once you find the review code, return to the terminal and run:

```bash
nyitsec-answer
```

Enter the code and submit the flag you receive.

**Temporary workspace:** Scripts and files saved in `/nyitsec-ctf` disappear when the challenge restarts. Keep anything important in `~/`.
