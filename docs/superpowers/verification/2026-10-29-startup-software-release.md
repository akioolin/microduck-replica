# Software 2026.10.29: release verification

This release imports the reviewed independent startup device-status change onto
the public software branch, without the separate unpublished music feature.
The existing image remains available; updating an existing card needs no reflash.

## Runtime and upgrade contract

- Native source: `0583a2a27e1f4cc719e1ac9dafbc1f0876616848`, published on the
  `fanhao375/Microduck-kissqy` fork's `hd1910-v167-startup-status-20261029` branch.
- ARM64 target: build `0791fcd-feetech-qinmo-control.46`, IPC 41,
  5,588,320 bytes, SHA256
  `3dbbf1723c0315afc15fd9f28787c0cfc194622a67802adcd1f5aa397ea47422`.
- The separately confirmed native installation accepts exact known .44/.45
  predecessors. Rollback verifies their original IPC 40 contract.
- A validated completed .44-to-.45 transaction, or its completed rollback, may
  precede the new transaction. The prior record is durably archived under the
  existing operation lock. Status reads do not modify the transaction/history.
  Incomplete, guarded, inconsistent or unknown legacy records remain refused;
  recovery belongs to the original signed updater, not a guessed new state.
- Stage one updates Studio/helper/voice. Stage two separately installs the native
  payload after explicit operator confirmation. Web rollback does not downgrade
  the native program. Movement and hardware calibration checks remain enforced.

## Checks completed before freezing source

- Metadata/transaction change: `4ae5422d4374895ade084d0daaa1f93996e03ec7`.
- Official Windows Python 3.13 focused aggregate: 176 tests, five platform skips,
  success. Includes native transactions, startup status, HTTP update boundaries,
  IMU redo and commissioning helper regressions. Native package tests: 3/3.
- Independent Linux Python 3.11 native transaction review: 88/88, no skips.
  Root's Linux Python 3.12 native plus native integration pair: 100/100, no skips.
- Full updater suite: 21 tests, four platform skips, success.
- Real failing regressions preceded target pin/API changes, predecessor rollover
  and archive retry durability. Independent review found the missing retry fsync;
  the fix and regression passed, with no remaining Critical/Important findings.
- The local feature's native suite, existing baseline failures and actual board
  readback are documented in [the device-status record](2026-10-29-startup-device-status.md).
  Its full native suite retains 20 pre-existing failures; it is not a full-green
  native test claim. The optional Python 3.12 Windows backend diagnostic exceeded
  its 100-second bound and is not counted as passing.

## Final packaging and publication evidence

- Frozen software source: `5b2c09cc95e93edcd8ae4be2d82b096d920ff2f1`.
- Official final Studio run: **1367 tests, 81 environment skips,
  success**, Python 3.13 isolated runner, `STUDIO_E2E=0`, 332.348 seconds.
  This run started after the final reviewed archive durability fix was committed.
- Root Linux updater suite: **21/21, no skips**, system Python 3.11. An earlier
  attempt using a private `/root` Python installation could not launch the test's
  demoted user; rerunning with the system interpreter passed without code changes.
- Signed outer package: `8079360` bytes, SHA256
  `2f002624cec39683434596145a985bf1ca1b42f2ea607f845b981cc3de428b26`.
- Frozen software archive SHA256: `7a9d78b58157edf021e252eec924eb3679379c71cee839f60221199b1655abc6`.
- Existing release public key retained; both signatures and the staged native
  identity were checked by the frozen old client and actual old ARM updater.
- All eleven local attachment hashes match GitHub's server size/digest records.
  The bootstrap's 319 file records were independently checked,
  including its exact signed package; only regular files/directories are present.
- Actual old ARM engine/QEMU checks passed: dry run, modified hash/signature
  refusal, apply, rollback, failed-health automatic rollback, killed-process
  durable recovery, managed native module trust and stage-one native isolation.

The frozen 20261027 client anonymously selected 2026.10.29 from the public
catalog, downloaded the package, and verified both signatures with its
original public key.

Published: [microduck-software-v2026.10.29](https://github.com/fanhao375/microduck-replica/releases/tag/microduck-software-v2026.10.29). The
`microduck-replica-image-20261027` release remains GitHub Latest. Existing cards
receive this software version through the software catalog or the offline bundle.
The two-stage native update and hardware acceptance limits above still apply.

Local evidence: `artifacts/software-release-20261029/` contains
`frozen-build.json`, `studio-full.log/json`, `runtime-provenance.json`,
`legacy-engine-final.json`, `local-assets-verification.json`,
`publication-assets.json` and draft/public verification reports. The public release
includes `runtime-provenance.json`, source links, all signatures and SHA256 files.
