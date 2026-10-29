# Startup device status: verification and local deployment

## Delivered behavior

Servo reachability and nullable raw feedback remain visible when IMU startup
fails. Startup observations are recorded in the existing native UART owner,
separately from atomic control samples. The original IMU, calibration, torque
confirmation and movement gates remain in force. There are no new serial probes.

The overview/onboarding/tuning/read-only servo table distinguish IMU waits from
generic bus waits, and responding, missing and unknown devices. Diagnostics
expire using native snapshot/check/reply/feedback ages plus Studio receipt age.
Diagnostic raw counts are not shown as calibrated joint angles or a live 3D pose.

## Frozen source and build

- Native base: `bdf494ab3fd74898b5159419fbffe87113b4097c`.
- Native implementation: `c995cb3a122f92e5f1218b00f790a239a56f5d3f`.
- Commissioning initialization follow-up: `0583a2a27e1f4cc719e1ac9dafbc1f0876616848`.
- Native IPC API: 41; build: `0791fcd-feetech-qinmo-control.46`.
- ARM64 binary: 5,588,320 bytes, SHA256
  `3dbbf1723c0315afc15fd9f28787c0cfc194622a67802adcd1f5aa397ea47422`.
- Native Git archive SHA256:
  `0132be369b9407829e3391a33199d9354db19b22621b9a062c9dc36f6d703c0e`.
- Studio implementation: `2792195602fb848b71436664121774bfc3d111a9`.
- Studio discovery-error copy follow-up: `6f8d2db595bbbea9d2fc80faa723b7c5778b0e07`.
- Scoped Studio patch SHA256:
  `d05d57a8878855e3fdaf8475fa88f2a1348248f89460d4f4597c3465ea573203`.

Rust 1.99.0 / zigbuild targeted `aarch64-unknown-linux-gnu.2.31` from the frozen
Git archive, with ten ONNX fixtures from the existing verified payload. ELF
inspection confirmed ARM64; the highest GLIBC symbol version was 2.30. QEMU
`--version`, `--help` and `deployment-info` passed. The linker emitted its existing
deprecated optimization-setting warning; this is not a warning-free-build claim.

## Software checks

- New observations and pending-readiness tests had real failing assertions before
  implementation, then passed. Frozen RPC evidence ages even when acquisition stops.
- Native Feetech: 86 passed; startup: 12 unit plus one integration passed;
  commissioning: 18 passed; PTY flows: five passed; HOME safeguards: seven passed.
- Full robotd baseline comparison retained the exact same 20 existing failures
  as clean `bdf494a`. The native full suite is not green; failure names and commands
  are documented in the native verification record. No control gates were weakened.
- Full Studio at `2792195`: 1,392 tests, 81 environment skips, success under
  `STUDIO_E2E=0 py -3.13 -X utf8 -I run_tests.py` (291.906 seconds).
- Targeted surrounding Studio checks: 223 passed. Node rendering helpers: four passed.
- The actual `IMU200: Feetech ID 200 response timeout` string reproduced two
  cross-mode copy failures. The follow-up matcher fixes them; all 17 startup/UI
  checks passed after that change. The full suite was not redundantly rerun for
  the one-line matcher change.
- A real native wire fixture passed through the patched older installed Studio
  source: 15 responding servos, startup posture retained, no calibrated angles or
  torque authority, and expired cached evidence returns unknown.

Independent specification and quality reviews approved the final changes. Review
found and led to fixes for commissioning initialization dropping observations and
the `IMU200` error matcher. The independent Studio reviewer rendered the real
ServoPage with partial/expired backend snapshots in headless Edge: correct counts,
distinct missing/unknown labels, disabled controls and no browser exceptions.

## Local board verification

The reused SD card on the replacement Radxa ZERO 3 is reachable at
`192.168.0.103`. Its existing params still select the absent host I2C LSM6DSV16X;
the physical ID 200 bus board separately answered earlier read-only diagnostics.
The configuration was deliberately preserved to test the reported fault.

Only the reviewed ARM64 executable and eleven scoped Studio source/browser files
were installed. Patch hunks were applied to downloaded copies of the actual older
installation so unrelated local music/Qinmo changes were not deployed. Imports
were checked against the live installation before replacing files.

The first attempt automatically rolled back when its fixed three-second web check
ran before the HTTP listener was ready. The transaction now checks actual
`/healthz` readiness with a bounded poll. A later user power cycle cleared temporary
staging; files were uploaded again. After another boot, only IMU 200 replied until
servo replies returned; the preflight prevented any replacement in that state.

The final transaction succeeded. All fifteen torque registers were read as zero
before replacement. Actual robotd API 41 and the patched, installed Studio modules
then reported:

- Servo summary: **15/15**, no missing rows; all fifteen raw position/voltage values present.
- Wait: **等待 IMU 数据（来源：lsm6dsv16x）**.
- Phase: `waiting_for_bus`; control ticks: zero; IMU ready: false.
- Native torque confirmation: false (OFF); physical controller service remains paused.
- Servo voltage range at verification: approximately 7.1–7.5 V; temperatures: 29–32 °C.
- `/healthz`, `/app.js`, `/servo.js`, `/startup-status.js`: HTTP 200, with the new helpers served.
- Original params and calibration SHA256 values remain unchanged.

This verifies the live fault is independently diagnosed; it does not validate
walking or authorize reusing the original duck's physical calibration.

## Evidence and rollback

Task evidence is under `artifacts/imu-only-20261029/`: source/build manifests,
`deployment-manifest.json`, scoped patch, `applied-hotfix-live.json`,
`live-verification.json`, and the bounded transaction scripts. No credentials are
included in release files or this document.

The successful board backup is:

`/var/lib/microduck-helper/manual-hotfix-backups/startup-status-20261029-a9dd4f48480248188acddcfc8c7088d9`

It contains original files, manifest and restore ownership/mode metadata. The
transaction rolls back replaced files on failure and restores the prior services.

This record describes the earlier scoped local deployment. The source branches
and artifacts are retained. Formal software 2026.10.29 carries the same reviewed
native binary with synchronized SHA/size/source, IPC 41 and verified .44/.45
predecessors; its packaging, installer compatibility and publication evidence are
recorded separately in `2026-10-29-startup-software-release.md`. No installer
allowlist was weakened for the local fix. No new SD image is required.
