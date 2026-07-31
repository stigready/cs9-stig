#!/usr/bin/env bash
# Re-run factory-style verify inside the role repo (apply role + OpenSCAP + score).
set -euo pipefail

ROLE_ROOT="${STIGFORGE_ROLE_ROOT:-/role}"
PROFILE="${STIGFORGE_PROFILE:?STIGFORGE_PROFILE required}"
RELEASE="${STIGFORGE_RELEASE:-local-prove}"
VERIFY_JSON="${ROLE_ROOT}/compliance/verify.json"

if [[ ! -f "$VERIFY_JSON" ]]; then
  echo "ERROR: missing ${VERIFY_JSON}" >&2
  exit 1
fi

read -r XCCDF DATASTREAM MIN_SCORE <<<"$(python3 - <<PY
import json
v=json.load(open("${VERIFY_JSON}"))
p=v["profiles"]["${PROFILE}"]
print(p["xccdf_profile_id"], p["ssg_datastream"], v["min_score"])
PY
)"

OUT_DIR="${STIGFORGE_OUT:-${ROLE_ROOT}/compliance/prove-runs/${RELEASE}/${PROFILE}}"
mkdir -p "$OUT_DIR"

echo "==> StigReady prove role=$(basename "$ROLE_ROOT") profile=${PROFILE} release=${RELEASE}"
echo "    xccdf_profile=${XCCDF}"
echo "    datastream=${DATASTREAM}"
echo "    out=${OUT_DIR}"

if command -v apt-get >/dev/null 2>&1; then
  apt-get update -qq || true
fi

PY="${ANSIBLE_PYTHON_INTERPRETER:-/usr/bin/python3}"
INV="$(mktemp)"
PLAY="$(mktemp)"
cat >"$INV" <<EOF
[prove]
localhost ansible_connection=local ansible_python_interpreter=${PY}
EOF
cat >"$PLAY" <<EOF
- hosts: prove
  become: true
  gather_facts: true
  any_errors_fatal: false
  vars:
    stigforge_profile: ${PROFILE}
  roles:
    - role: ${ROLE_ROOT}
EOF

echo "==> ansible-playbook apply"
set +e
ansible-playbook -i "$INV" "$PLAY" 2>&1 | tee "$OUT_DIR/ansible.log"
ansible_rc=${PIPESTATUS[0]}
set -e
echo "ansible_rc=${ansible_rc}" | tee "$OUT_DIR/ansible.rc"

DATASTREAM_PATH="/usr/share/xml/scap/ssg/content/${DATASTREAM}"
if [[ ! -f "$DATASTREAM_PATH" ]]; then
  DATASTREAM_PATH="/ssg/${DATASTREAM}"
fi
if [[ ! -f "$DATASTREAM_PATH" ]]; then
  echo "ERROR: SCAP datastream not found: ${DATASTREAM}" >&2
  exit 1
fi

echo "==> oscap eval"
set +e
oscap xccdf eval \
  --profile "$XCCDF" \
  --results "$OUT_DIR/results.xml" \
  --results-arf "$OUT_DIR/arf.xml" \
  --report "$OUT_DIR/report.html" \
  "$DATASTREAM_PATH"
oscap_rc=$?
set -e
echo "oscap_rc=${oscap_rc}" | tee "$OUT_DIR/oscap.rc"

if [[ ! -f "$OUT_DIR/results.xml" ]]; then
  echo "ERROR: oscap produced no results.xml" >&2
  exit 1
fi

echo "==> score gate (min=${MIN_SCORE})"
python3 "${ROLE_ROOT}/scripts/score-results.py" \
  --results "$OUT_DIR/results.xml" \
  --verify-json "$VERIFY_JSON" \
  --profile "$PROFILE" \
  | tee "$OUT_DIR/score.stdout"
score_rc=${PIPESTATUS[0]:-$?}

echo "==> prove complete → ${OUT_DIR}"
exit "${score_rc:-0}"
