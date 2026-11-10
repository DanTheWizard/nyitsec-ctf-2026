# Hidden in Plain Sight

**Difficulty: Easy** | **Skill: Identifying file formats**

The NYITSec team received an attachment called `notice.txt`. A regular text editor cannot display it properly.

**Goal:** Find the phrase hidden in the attachment and enter it exactly, including capitalization and symbols.

Your files are in the writable `/nyitsec-ctf` workspace.

### Investigate

Try looking at the file's type:

```bash
ls
file notice.txt
```

You can also use **Workspace → Code (VS Code)** or **Workspace → Desktop** to examine the file.

- In **VS Code**, choose **File → Open Folder** and enter `/nyitsec-ctf`.
- In **Desktop**, open the file manager and browse to `/nyitsec-ctf`.

**Hint:** A filename extension does not guarantee a file's actual format. If an image viewer refuses to open `notice.txt`, try making a copy with the correct extension.

### Submit

Run `nyitsec-answer`, enter the phrase you find, and submit the flag you receive.

**Temporary workspace notice:** Files created in `/nyitsec-ctf` disappear when the challenge restarts. Copy important work to `~/` to keep it.
