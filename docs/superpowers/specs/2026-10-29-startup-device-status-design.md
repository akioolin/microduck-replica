# Independent startup device status

The user requires servo reachability to remain visible when the configured IMU is
unavailable. The live replacement board responds at IDs 10–14, 20–24, 30–34 and 200;
its reused SD card selects the missing host I2C IMU. All fifteen torque registers
read zero. Robotd remains at `waiting_for_bus` with zero control ticks. No source,
calibration, home, motion or firmware-selection changes are part of this fix.

## Chosen approach

Preserve validated replies as independent diagnostic observations inside the sole
native UART owner. Publish those observations during startup failures and successful
reads that are still waiting for IMU readiness. Studio consumes this evidence for
the servo counter and read-only servo table. Existing motion eligibility, atomic
sensor samples, torque confirmation and IMU checks retain their meaning.

A Studio serial scanner would compete with robotd and is rejected. Reusing the
one-off scanner's saved output would be stale and is also rejected.

## Native wire contract

`robot.busStatus.native.servo_observations` is an object containing:

- `attempted`: boolean, at least one requested servo reply was checked.
- `age_ms`: age of this observation snapshot at response time; it must increase
  even if the control thread ceases publishing while IPC remains responsive.
- `rows`: one row per configured servo, in configured joint order. Each row has
  `id`, `name`, `responding` (true/false/null for answered/missed/not checked),
  `reply_age_ms`, `feedback_age_ms`, and nullable telemetry fields
  `position_raw`, `speed_raw`, `load_raw`, `current_raw`, `volts`,
  `temperature_c`. Ages are measured at snapshot capture; add snapshot `age_ms`
  when determining freshness. Null values are never fabricated as zero.

Only checksum-valid replies from requested IDs provide response evidence. A
torque read proves presence, without pretending it contains positions or voltage.
Validated 56/15 telemetry can supply those values even if the same transaction
later fails due to another missing device, an invalid IMU or a missing host sample.
An unanswered latest request changes responding to false; unrelated reads do not
refresh old servo evidence. Missing/unsupported IMUs never become usable samples.

Publish `native` diagnostics on every relevant startup wait, including initialization
failure after opening the bus and pose adoption failures. Diagnostic-only data
must not populate control caches, release startup gates, enable policy, write
goals, or provide emergency-stop confirmation. API version becomes 41; clients log
version differences rather than refusing them. Build identifier ends in `.46`.

## Studio behavior

During startup, a fresh observation yields the responding servo count and available
feedback values. Each observation and telemetry value expires after 3000 ms,
including if busStatus keeps returning the same captured snapshot. Failed or
disconnected IPC never makes old observations fresh. Unknown is displayed as
unknown, not zero devices. Normal motion and commissioning data retain priority
outside startup.

The servo page lists responding/missing/unknown per ID and uses nullable raw
feedback without treating it as calibrated angles. Existing controls stay gated
by posture and native motion checks. No active serial fallback is added.

Startup errors naming IMU/host IMU must read `等待 IMU 数据` and show the configured
source when available, rather than guessing servo power is off. The onboarding
header, commit readiness and tuning phase labels must not contradict this. Generic
bus waits say `等待总线设备响应`, with raw error retained. No password or model changes.

## Verification and delivery

Regression tests first reproduce all-servos-plus-missing-host-IMU, missing bus IMU,
partial servo replies, invalid reply checksums, stale cached observations and no
observations. Existing motion permission and atomic sample tests remain passing.
Studio tests verify counter, raw table, nullable values, expiry and accurate copy.

Build a pinned ARM64 binary, inspect its ABI and run it under QEMU, then review
native and Studio changes. Back up live binaries/modules and original configs;
deploy only reviewed hotfix files after verifying all fifteen servos are limp and
no serial owner is competing. Keep the deliberately missing I2C source to validate
that real servos are displayed independently. Confirm no target/torque-enable
traffic and no changes to the calibration or IMU source. Preserve rollback files.
