# Changelog

Format based on [Keep a Changelog](https://keepachangelog.com/).

## [0.3.0] - 2026-09-12

### Changed
- StigForge export refresh for `cs9_stig` at `0.3.0`.

### Verified (OpenSCAP)

- **`stig`** — score **94.2%** (floor 90.0%) · gate **PASS** · evidence `20260912T130305Z`
  - Remaining counted failures: `configure_crypto_policy, file_permissions_ungroupowned, network_configure_name_resolution, use_pam_wheel_for_su`

### Provenance

- Factory pipeline: https://github.com/stigready/stigforge/actions/runs/34693316989
- Factory commit: `562a1f7c1a8e19235ee26e972174d1be6c88998c`

## [0.2.4] - 2026-07-31

### Added
- Initial StigForge export of matrix role `cs9_stig`.
- OpenSCAP verify evidence bundles per profile under `compliance/releases/`.

### Verified (OpenSCAP)

- **`stig`** — score **97.14%** (floor 90.0%) · gate **PASS** · evidence `20260731T090012Z`
  - Remaining counted failures: `file_permissions_ungroupowned, network_configure_name_resolution`

### Provenance

- Factory pipeline: https://github.com/stigready/stigforge/actions/runs/30617333526
- Factory commit: `5c2fc8f5ad23bdd66e77fe95e1363d5a10c9f05d`

## [0.2.1-private-review] - 2026-07-28

### Changed
- Galaxy-style layout: Ansible role at repository root; evidence under `compliance/`.
- Private review tag `v0.2.1-private-review` (supersedes nested `roles/<role>/` export).

## [0.2.0-private-review] - 2026-07-26

### Added
- First private StigForge export to `stigready/*` (factory review; nested role path).
