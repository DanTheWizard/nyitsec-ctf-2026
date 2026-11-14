"""Consistency checks for the officer-only, known-answer QA documentation.

No pwn.college flags or real credentials are included. These are synthetic
challenge answers, kept in private GitHub outside deployable directories.
"""
from pathlib import Path
import re
import runpy
import unittest

ROOT = Path(__file__).resolve().parents[1]
CASES = [
    [
        "fundamentals/incident-id",
        [
            "NY-106"
        ],
        [
            "NY-105"
        ]
    ],
    [
        "fundamentals/base64-basics",
        [
            "NYITSEC-BASE64-START-26"
        ],
        [
            "NYITSEC-BASE64-START-25"
        ]
    ],
    [
        "fundamentals/base64-layers",
        [
            "NYITSEC-THREE-LAYERS-26"
        ],
        [
            "NYITSEC-THREE-LAYERS-25"
        ]
    ],
    [
        "fundamentals/base64-more",
        [
            "Super Cool"
        ],
        [
            "Super Cool!"
        ]
    ],
    [
        "fundamentals/password-audit",
        [
            "Welcome2026!"
        ],
        [
            "Welcome2026"
        ]
    ],
    [
        "level-2/cookie-metadata",
        [
            "COOKIE-TRACE-26"
        ],
        [
            "COOKIE-TRACE-27"
        ]
    ],
    [
        "level-2/forgotten-file",
        [
            "NYITSEC-LOST-26"
        ],
        [
            "NYITSEC-LOST-25"
        ]
    ],
    [
        "level-2/inspect-source",
        [
            "NYITSEC-SOURCE-26"
        ],
        [
            "NYITSEC-SOURCE-27"
        ]
    ],
    [
        "level-2/misnamed-image",
        [
            "ThePassword#LOL"
        ],
        [
            "ThePassword#LOLx"
        ]
    ],
    [
        "level-2/steg-photo",
        [
            "PHOTO-CRUMB-26"
        ],
        [
            "PHOTO-CRUMB-25"
        ]
    ],
    [
        "level-3/broken-login",
        [
            "OrbitingToaster#73"
        ],
        [
            "OrbitingToaster#74"
        ]
    ],
    [
        "level-3/dns-treasure-hunt",
        [
            "The red lantern waits by the harbor"
        ],
        [
            "The blue lantern waits by the harbor"
        ]
    ],
    [
        "level-3/forgotten-commit",
        [
            "Paper satellites still orbit"
        ],
        [
            "Not the recovery phrase"
        ]
    ],
    [
        "level-3/packet-detective",
        [
            "bob",
            "Lumen&Branch#47"
        ],
        [
            "bob",
            "not-the-password"
        ]
    ],
    [
        "level-3/suspicious-script",
        [
            "B",
            "IKnowPythonDeobfuscation#404"
        ],
        [
            "A",
            "IKnowPythonDeobfuscation#404"
        ]
    ]
]
class OfficerQAKnownAnswerTests(unittest.TestCase):
    def test_guides_and_checker_inputs(self):
        for rel, correct, incorrect in CASES:
            with self.subTest(challenge=rel):
                guide = (ROOT / "docs" / "officer-solutions" / f"{rel}.md").read_text(encoding="utf-8")
                self.assertIn("## Officer QA: verified answer and repeatable solution", guide)
                self.assertIn("### Reproduce the intended solution", guide)
                self.assertIn("### Noninteractive checker test over SSH", guide)
                self.assertFalse((ROOT / rel / "README.md").exists())
                # Do not write plaintext officer answers into student descriptions.
                description = (ROOT / rel / "DESCRIPTION.md").read_text(encoding="utf-8")
                for secret in correct:
                    self.assertIn(f"`{secret}`", guide)
                    self.assertNotIn(secret, description)
                if rel == "fundamentals/incident-id":
                    events = (ROOT / rel / "events.log").read_text().splitlines()
                    matches = []
                    for line in events:
                        fields = dict(part.split("=", 1) for part in line.split() if "=" in part)
                        if all(fields.get(key) == value for key, value in (
                            ("service", "ssh"), ("source", "external"), ("status", "blocked")
                        )):
                            matches.append(fields["event"])
                    self.assertEqual(matches, correct)
                else:
                    check = runpy.run_path(str(ROOT / rel / "verify"), run_name="officer-qa-test")["is_correct"]
                    self.assertTrue(check(*correct), f"{rel}: documented answer rejected")
                    self.assertFalse(check(*incorrect), f"{rel}: documented wrong input accepted")

if __name__ == "__main__":
    unittest.main()
