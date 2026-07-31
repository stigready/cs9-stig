#!/usr/bin/env bash
# Reproduce factory OpenSCAP verify for a pinned release (requires Docker).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

RELEASE="${RELEASE:-}"
export RELEASE
if [[ -z "$RELEASE" ]]; then
  if [[ -f compliance/verify.json ]]; then
    RELEASE="$(python3 -c "import json; print(json.load(open('compliance/verify.json'))['release'])")"
  fi
fi
if [[ -z "$RELEASE" ]]; then
  echo "Usage: RELEASE=<version> $0   # e.g. RELEASE=0.2.1-private-review" >&2
  echo "  or set release in compliance/verify.json" >&2
  exit 1
fi

if ! command -v docker >/dev/null 2>&1; then
  echo "ERROR: Docker is required for full prove (apply role + OpenSCAP in a clean image)." >&2
  echo "See compliance/README.md for scoring an existing results.xml without Docker." >&2
  exit 1
fi

VERIFY="$ROOT/compliance/verify.json"
TAG="$(python3 -c "import json; print(json.load(open('$VERIFY'))['docker_image_tag'])")"
mapfile -t PROFILES < <(python3 -c "import json; print('\n'.join(json.load(open('$VERIFY'))['profiles']))")

echo "==> building prove image ${TAG}"
docker build -f "$ROOT/compliance/docker/Dockerfile" -t "$TAG" "$ROOT"

rc=0
for p in "${PROFILES[@]}"; do
  echo "==== prove ${RELEASE} / ${p} ===="
  if ! docker run --rm --privileged \
    -v "$ROOT:/role" \
    -e STIGFORGE_PROFILE="$p" \
    -e STIGFORGE_RELEASE="$RELEASE" \
    "$TAG"; then
    rc=1
    continue
  fi
  if ! python3 "$ROOT/scripts/score-results.py" --compare --profile "$p" --release "$RELEASE" --repo-root "$ROOT"; then
    rc=1
  fi
done

if [[ "$rc" -eq 0 ]]; then
  echo "==> prove OK for release ${RELEASE}"
else
  echo "==> prove FAILED for release ${RELEASE}" >&2
fi
exit "$rc"
