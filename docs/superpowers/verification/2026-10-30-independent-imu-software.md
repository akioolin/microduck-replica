# Independent IMU diagnostics: software release verification

The user requested normal web identification with only the ID 200 IMU connected.
The existing complete-robot torque and movement checks remain unchanged. The
same native UART owner now collects bounded read-only startup evidence separately
from control samples, including when structurally valid calibration refuses motion.
Unknown/malformed configuration is not repaired or guessed by diagnostics.

## Reviewed source and artifact

- Native: `931ce978f2efb27c157b7a583ee402793131a0d2`, based on
  `0583a2a27e1f4cc719e1ac9dafbc1f0876616848`.
- Public branch: `fanhao375/Microduck-kissqy`,
  `hd1910-v167-independent-imu-20261030`.
- Frozen native archive SHA256:
  `97b78fb25d8a447e6d4bf357cea9c45400da2e7b1e51a942f9ee18ee76c7d274`.
- ARM64: 5,606,976 bytes, SHA256
  `725b74cd93660a312970a44879abe5b75e8becf108499a1b8798961e48ca5f00`.
- Build `0791fcd-feetech-qinmo-control.47`, IPC 42, official 0.15.1/model API 2.
- Studio: `c1db349`, followed by current-bus/hello cache fix `29d5342`.
- Native updater: `dae3d2e3aa73c86487f520a1101fb703870875ea`.

Rust 1.99.0/zigbuild used the clean committed Git archive, target
`aarch64-unknown-linux-gnu.2.31`, release codegen-units 1 and the ten previously
verified ONNX fixtures. ELF is AArch64 PIE; maximum GLIBC symbol is 2.30. Actual
ARM64 `--version`, `--help`, and `deployment-info` passed under QEMU. The existing
deprecated linker optimization warning remains; this is not a warning-free claim.

## Feature and transaction checks

Native TDD first reproduced missing observations with only IMU/no servos. Additional
failing cases reproduced identity surviving a missing sample, early calibration
refusal preventing observation, and a replaced report inheriting old capture state.
Final native results: new control 6/6, new startup integration 2/2, Feetech 92/92,
commissioning 7/7, startup guards 7/7, RPC capture age 1/1, IPC 54/54. Tests use
real Linux PTYs, not real hardware. One initial existing model test lacked its ignored
ONNX fixture; restoring the approved fixture made the 92-test run pass. Full native
workspace was not rerun; its inherited test/formatting baseline is not a green claim.
Commands are in the native `verification/independent-startup-imu-20261030.md`.

Studio TDD and review caught conflicting profile metadata, nullable DXL2/sample
flags, browser reconnect/phase caches and a new native hello reviving prior normal
control metadata. Final focused 43 tests passed; independent POSIX IMU/backend/
calibration checks 113/113, actual Edge IMU/Main/wizard 13/13 and Node unit 5/5.
An isolated full overview E2E run at `c1db349` passed 21 tests in 139.580 seconds,
with both browser error arrays empty; an earlier navigation timeout did not recur.
The final hello-context follow-up has its own failing/passing actual Main regression.

Updater actual-artifact RED preceded .47 pins. Windows native/bridge: 112 tests,
five platform skips, success; POSIX native/bridge: 112/112. Independent combined
POSIX review: 140/140; full updater POSIX: 21/21. Known predecessors .44/.45/.46
retain API 40/40/41 rollback checks. Only actual known legacy journal pairs can
roll over after exact terminal/installed-byte checks and durable raw-record archival;
incomplete old transactions still require their original signed updater.

Independent specification and code-quality reviews report no remaining Important
or Critical findings. Diagnostic evidence cannot authorize motion, calibration,
mounting, torque, a calibrated pose or an automatic source change.

## Final packaging and publication

- Frozen software source: `2ba8e5d8ae4a4cf42f6284baf5dd817b412c4a5d`.
- Official isolated Python 3.13 full Studio: **1392 tests, 81 environment
  skips, success**, 329.338 seconds, `STUDIO_E2E=0`. The final runtime code was
  stable before this run; the following source commit adds release documentation.
- Signed outer package: 8089600 bytes, SHA256
  `880803ef4143913e75e1f12b27ff75268c124dd4dbff4676b3dd6646779831b9`.
- Frozen software archive SHA256: `e797b0a08a5ae7a0de3115e399a66c4316e33f8075be9d189590cb8a67559808`.
- Both minisign signatures and exact native payload/module trust were checked by
  the old ARM engine. Dry run, tampered hash/signature refusal, apply, rollback,
  failed-health rollback and killed-process durable recovery passed in temporary
  roots under QEMU. Stage one leaves the installed robotd untouched and restarts
  only Studio/voice. This is not physical automatic-install acceptance.
- All eleven local attachment hashes/sizes match GitHub server digests. The
  bootstrap's 319 individual files, executable mode,
  exact signed package, regular-file paths and original public key were checked.

The frozen 20261027 client anonymously selected 2026.10.30 from the public
catalog, downloaded the package, and verified both signatures with its
original public key.

Published: [microduck-software-v2026.10.30](https://github.com/fanhao375/microduck-replica/releases/tag/microduck-software-v2026.10.30). The
`microduck-replica-image-20261027` image remains GitHub Latest. Existing compatible
cards use the normal software catalog or offline bundle; no new image is required.
The first-stage readiness conditions and separately confirmed native replacement
still apply, as described in the user instructions.

Evidence in `artifacts/software-release-20261030/`: `frozen-build.json`, full Studio
log/result, runtime provenance, old-engine verification, local attachment inventory,
and draft/public GitHub verification. Public attachments include signatures, SHA256
files and `runtime-provenance.json` with exact source/artifact identities.

This task did not deploy the new feature to a live device or validate an actual
IMU-only board setup. Physical upgrade and walking acceptance are not claimed.
