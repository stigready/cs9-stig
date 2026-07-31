# Verify OpenSCAP scores in this role repo

Each release ships **immutable evidence** under `compliance/releases/<version>/<profile>/`
(`score.json`, `results.xml`, `report.html`, `evidence.json`).

You can **re-check the score** in two ways:

## 1. Full reprove (recommended — matches factory docker verify)

Requires **Docker**. Applies this role in a clean OS image, runs OpenSCAP, and scores with the
same exempt-rule policy as StigForge (`compliance/exempt-rules.txt`).

```bash
make prove RELEASE=0.2.1-private-review
# or
RELEASE=0.2.1-private-review ./scripts/prove.sh
```

Outputs go to `compliance/prove-runs/<release>/<profile>/` and are compared to the pinned
`score.json` for that release.

## 2. Score your own OpenSCAP results

If you already applied the role and ran `oscap xccdf eval` on a host:

```bash
python3 scripts/score-results.py \
  --results /path/to/results.xml \
  --profile stig \
  --verify-json compliance/verify.json
```

Compare to the published release:

```bash
python3 scripts/score-results.py --compare --profile stig --release 0.2.1-private-review
```

(after a local `make prove`, or point `--results` at your own file without `--compare`)

## Configuration

- `compliance/verify.json` — profiles, XCCDF ids, datastream names, floor score
- `compliance/docker/Dockerfile` — OS image used for reprove (family-specific at export)

Optional: `pip install defusedxml` on the host for safer XML parsing when scoring outside Docker.
