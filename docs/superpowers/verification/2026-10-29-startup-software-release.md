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

## Packaging and publication evidence

The official full Studio run, frozen source/package hashes, verified resource
inventory, signed package/legacy ARM engine checks, draft attachment hashes and
anonymous old-client discovery/download are recorded during publication under
`artifacts/software-release-20261029/`. A final evidence update will record their
actual outcomes and the published source revision. No private signing key, API
key, pairing state or personal calibration belongs in these release attachments.

The feature has local board evidence, with all 15 servos visible while the chosen
I2C IMU has no sample, control ticks remain zero and torque is off. The formal
automatic installer is exercised separately in temporary roots/QEMU; no automated
physical install or walking acceptance is implied.
