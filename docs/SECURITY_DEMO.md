# Security demo fixtures

These findings are intentional demo fixtures. They are not product defects. The application does not import `app/demo_findings.py` or `python-jose`, and its onboarding behavior is unchanged.

| Finding | Where | Scanner | Note |
| --- | --- | --- | --- |
| `python-jose==3.3.0` | `requirements.txt` | Trivy, on the image | [CVE-2024-33663](https://github.com/advisories/GHSA-6c5p-j8vq-pqhj) (GHSA-6c5p-j8vq-pqhj). GitHub Advisory Database rates it Critical. Versions below 3.4.0 are affected. The app does not import this package. |
| Hardcoded fake API key `sk_test_FAKE_DEMO_KEY_0000000000` | `app/demo_findings.py` `sign_demo` | Semgrep `python.jwt.security.jwt-hardcode.jwt-python-hardcoded-secret` | Not a real credential. `sign_demo` is never called. |
| MD5 checksum | `app/demo_findings.py` `checksum` | Semgrep `python.lang.security.insecure-hash-algorithms-md5.insecure-hash-algorithm-md5` | Used only as a non-security checksum. `checksum` is never called. |
| `subprocess.run("echo demo", shell=True)` | `app/demo_findings.py` `echo_demo` | Semgrep `python.lang.security.audit.subprocess-shell-true.subprocess-shell-true` | `echo_demo` is never called. That rule skips a constant command string, so `p/python` and `p/owasp-top-ten` do not report this line. |

`semgrep --config p/python --config p/owasp-top-ten` reports the API key and the MD5 checksum.
