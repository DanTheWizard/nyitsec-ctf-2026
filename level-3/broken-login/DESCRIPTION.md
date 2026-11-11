# The Broken Login

**Mission:** A fictional forum has gone out of control. Your investigation team wants you to find its **Nuke authorization password** so the test forum can be shut down.

This is an **authorized, intentionally vulnerable training website running only inside your specially crafted pwn.college VM**. All accounts, posts, email addresses, and database records are fictional. Use only this local lab, never a real website.

### Open the forum

1. Select **Workspace → Desktop** and open **Firefox**.
2. Go to **http://nyitsecwebsite.test/**.
3. Explore the forum, its signup waiting list, and its member login.

**Recon team hint:** Several input fields were not properly sanitized before being inserted into SQL queries. The signup queue and the administrator login might both be worth investigating. Think about what an unsafe query could let you do.

An administrator can access the **Nuke Forum** button in the top-right corner. Follow the confirmation process to recover the password.

**Alternative solutions are welcome:** If you find another route to recover valid administrator credentials or gain administrator access using the lab's vulnerable inputs, that counts too.

Once you have the **Nuke authorization password**, return to the terminal:

```bash
nyitsec-answer
```

**If you make a major mistake**, such as deleting something required to continue, use **Reset Challenge** in pwn.college to restore the fictional website and its database.

**Temporary workspace:** Files in `/nyitsec-ctf` are not preserved after a challenge restart. Save notes to `~/` if needed.
