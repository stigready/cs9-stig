# cs9_stig — Ansible role (cs9-stig)

**Ansible hardening role** for **CentOS Stream 9** (DISA STIG). Suitable for playbooks, Packer/Ansible provisioners, and golden-image pipelines. Search keywords: `ansible`, `ansible-role`, `centos`, `centos-stream`, `compliance`, `cs9`, `devsecops`, `disa`, `disa-stig`, `hardening`, `infrastructure`, `openscap`, `rhel`, `security`.

StigForge-exported Ansible role **`cs9_stig`** · release **`0.3.42`**.
Matrix cell status: **`green`**.

## Install (Ansible Galaxy)

This repository root **is** the Ansible role (Galaxy-style layout). OpenSCAP evidence
lives under `compliance/` and is not loaded when the role runs.

From **Ansible Galaxy** (after import; namespace `stigready`):

```bash
ansible-galaxy role install stigready.cs9_stig,0.3.42
```

From **GitHub** (public):

```yaml
# requirements.yml
roles:
  - src: https://github.com/stigready/cs9-stig
    scm: git
    version: v0.3.42   # or an immutable commit SHA
    name: cs9_stig
```

```bash
ansible-galaxy role install -r requirements.yml -p ./roles
ansible-playbook -i inventory site.yml   # role: cs9_stig
```

## Verification status (this release)

Evidence was produced by **docker verify + OpenSCAP** on the factory CI run cited below.

| Profile | Score | Floor | Gate | Ansible | Evidence tested (UTC) |
|---|---:|---:|---|---|---|

Full artifacts per profile: `compliance/releases/0.3.42/<profile>/` (`score.json`, `results.xml`, `arf.xml`, `evidence.json`, `evidence-report.html`, `poam.md`).

## Reports & review

- **[REVIEW.md](REVIEW.md)** — linked evidence index for product owner review
- **[reports/index.html](reports/index.html)** — HTML report index
- **[CHANGELOG.md](CHANGELOG.md)** — release notes and verify summary

## Verify the score (customer)

Re-run OpenSCAP in Docker and compare to this release's evidence:

```bash
make prove RELEASE=0.3.42
```

Or score your own `results.xml`: see **[compliance/README.md](compliance/README.md)**.

## License

- **[LICENSE](LICENSE)** (MIT) — StigForge export packaging
- **[NOTICE](NOTICE)** — ComplianceAsCode / BSD-3-Clause task body attribution

## Factory

- Monorepo: [stigready/stigforge](https://github.com/stigready/stigforge) @ `e07f386623f1f6fbecefcc1435539bc9a175cfdd`
- CI run: https://github.com/stigready/stigforge/actions/runs/39294275173
- Catalog: [https://stigready.com/#stigforge](https://stigready.com/#stigforge)

