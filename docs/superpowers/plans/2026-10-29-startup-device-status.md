# Independent startup device status implementation plan

> For agentic workers: use subagent-driven-development for the independent native
> and Studio tasks, with specification review followed by code quality review.

**Goal:** Display actual servo replies while IMU failure still blocks motion.

**Architecture:** Capture observations in the existing native UART owner; expose
the design's `native.servo_observations` contract during startup; consume it in
Studio without changing the control sample or motion checks.

**Tech stack:** Rust robotd/duck-control, Python Studio, existing web components,
WSL Rust 1.99 and zigbuild, pytest/unittest, local SSH hardware verification.

## Task 1: Native observations and startup publication

Files: `duck-control/src/feetech.rs`, a focused observation module if needed,
`robotd/src/main.rs`, `robotd/src/feetech_commissioning.rs`,
`duck-ipc-proto/src/lib.rs`, and native mechanism documentation. Root is
`F:/chengshenzhilu/Robot/Microduck/.worktrees/startup-native-20261029/microduck-hd1910/firmware`.

- [x] Add failing serial-peer regressions: valid servo replies plus no host sample
  still return an IMU error but expose fifteen fresh observations; no bus IMU and
  partial/malformed replies preserve only validated servo presence; frozen IPC
  snapshot ages; observations never satisfy all-joints/control-sample gates.
- [x] Run focused tests and record their expected assertion failures.
- [x] Capture validated reply observations without changing transaction results.
  Serialize exactly the nullable fields defined in the design; use native sample
  times and age snapshots at IPC response time.
- [x] Publish the diagnostic object on startup failure paths and pending-readiness
  paths. Keep torque-off, verification, atomic samples and retry scheduling intact.
- [x] Set API 41 and `.46` build metadata. Update the owning mechanism document.
- [x] Run focused regressions and relevant existing core/startup/motion tests.
  Test command: `cargo +1.99.0 test -p duck-control feetech -- --test-threads=1`;
  robotd tests use their existing focused startup filter and one test thread.
- [x] Self-review and commit the native change; provide the wire fixture and
  red/green test evidence to the coordinator.

## Task 2: Studio consumes independent observations

Files: `software/studio/studio/state.py`, `servo.py`, `onboard.py`, `commit.py`,
`tune.py`, a shared `startup_status.py` helper if useful, `robotd.py`, relevant
Python tests and minimal existing web rendering. Worktree is this plan's repository.

- [x] Add failing tests for fresh observations during host IMU failure, partial
  responses, unknown values, aged snapshots, stale IPC, and ordinary motion data.
  Fixture: `native.servo_observations = {attempted: true, age_ms: 0, rows: [...]} `,
  each row uses the exact nullable fields in the design, including `check_age_ms`
  for latest attempted READ and `reply_age_ms` for last valid response.
- [x] Run those tests and confirm failures are caused by the missing feature.
- [x] Normalize the native observations without opening serial ports. A row is
  responding only with fresh native and IPC evidence; feedback is fresh only if
  its own age also passes 3000 ms. Missing fields remain null.
- [x] Reuse normalized evidence for servo counter and read-only servo table.
  Fix startup IMU copy consistently across onboarding/commit/tuning surfaces.
  Controls and calibration readiness retain their existing gates.
- [x] Set Studio expected API 41. Run targeted state/servo/onboarding/commit/tune
  tests, then the existing full Studio suite once. Self-review and commit.

## Task 3: Integration, review and board hotfix

- [x] Review native contract against Studio fixture and stale semantics; run an
  integration fixture through real Studio state serialization and rendering.
- [x] Obtain specification and quality reviews, repair actionable findings with
  regression tests, then rerun affected checks only.
- [x] Export the reviewed native commit with canonical LF; supply verified ONNX
  fixtures from the existing pinned build payload. Build with
  `cargo +1.99.0 zigbuild --locked --release --jobs 2 --target aarch64-unknown-linux-gnu.2.31 -p robotd --bin robotd`.
- [x] Inspect ELF architecture/GLIBC requirements and QEMU `--version`, `--help`,
  and `deployment-info`; record source and binary SHA256.
- [x] Identify installed Studio paths. Back up only replaced files and the native
  binary, and record checksums of original config/calibration.
- [x] Confirm fifteen torque registers are zero and no calibration/update job is
  active, stop services, atomically replace reviewed hotfix files, start robotd
  and Studio, and leave the physical controller paused for this bench session.
- [x] With the original I2C source still absent, verify real busStatus/Studio report
  fifteen responding servos and the IMU-specific wait, without control ticks,
  goal writes or torque enabling. Verify snapshot expiry in a controlled fixture.
- [x] Write verification/rollback notes and report the actual tested result.
