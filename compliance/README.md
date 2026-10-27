# Scoring this role

This repository ships **no OpenSCAP results**. A container cannot evaluate most hardening rules, so the role
is not scored here. `compliance/releases/<version>/manifest.json` records this for each release.

## Score a host you hardened

Apply the role to a host, then run OpenSCAP on that host with the SCAP Security Guide (SSG) release named
in `compliance/verify.json` (`ssg_version`, the release this role was generated from), using the datastream
and profile named there:

```bash
sudo oscap xccdf eval --profile <xccdf_profile_id> --results results.xml <ssg-datastream.xml>
```

Score the results with this role's exception list (`compliance/exempt-rules.txt`):

```bash
make score-results RESULTS=results.xml PROFILE=stig
# or
python3 scripts/score-results.py --results results.xml --profile stig --verify-json compliance/verify.json
```

`score-results.py` parses the results with `defusedxml` when it is installed (`pip install defusedxml`) and falls
back to the standard library XML parser otherwise.

## Files

- `compliance/verify.json`: profiles, XCCDF ids, datastream names, SSG version, floor score
- `compliance/exempt-rules.txt`: rules excluded from the score, each explained in the README's *Exceptions* table
- `compliance/releases/<version>/manifest.json`: what each release contains
