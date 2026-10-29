# Independent startup IMU diagnostics

User-approved goal: with only the configured ID 200 bus IMU connected, the normal
web console identifies the board and distinguishes its diagnostic response from
missing servos. No extra serial owner or service-mode switch is required.

Root cause: motion `confirm_startup_limp` and commissioning initialization verify
all configured servo torque-off states before identifying the bus IMU. An early
servo failure prevents identification. Keep those motion gates exactly as they
are, and collect read-only IMU observations through that same startup UART owner
when initialization is waiting. Preserve the original startup refusal.

## Native diagnostic contract

`robot.busStatus.native.imu_observation` is optional and diagnostic-only:

```
{
  "source": "bus", "attempted": true, "responding": true,
  "age_ms": 0,
  "info": {"protocol": "feetech", "board": "imu_to_dxl", "identity": [],
           "profile": "legacy"},
  "sample_valid": true, "sensor_ready": true,
  "sample_fresh": null, "sequence": 1, "error": null
}
```

`info` uses the existing complete BusImuInfo shape. Null/absent values mean unknown.
`sample_valid` validates a decoded sample; `sensor_ready` is the board status;
`sample_fresh` must not claim freshness without sufficient evidence. Observation
age increases on repeated RPC replies even when acquisition stops. A response
does not imply a valid sample, verified mounting, torque-off or motion readiness.

Only the selected bus profile/transport is used (legacy auto Feetech/DXL2, or
explicit Qinmo). Never silently switch an I2C-selected system to the bus source.
No goals, gains, torque-on, calibration writes or new UART owner are introduced.
Do not move IMU identity checks ahead of the existing torque safety check as a
replacement for that check. Native API becomes 42/build control.47, with docs
and matching install consequences.

## Web behavior

Overview and IMU page show independent diagnostic reachability/board/protocol.
They distinguish identified/sample available, identified/data waiting or invalid,
no response, stale and unknown. Add native observation age and Studio receipt age
before trusting evidence (3 seconds); disconnect/error invalidates it. Metadata
from a previous profile, source, daemon or expired capture cannot become current.
Use a separate diagnostic status, never overwrite control `ready`, mounting
verification, calibrated 3D pose, calibration capture eligibility or movement gates.
Existing complete-robot behavior remains. Older daemons without the field remain
unknown rather than guessed missing or healthy.

## Acceptance and delivery

TDD: only IMU; no devices; partial servos+IMU; all servos+missing/invalid IMU;
unknown identity/profile mismatch; frozen or expired evidence; real UART owner
read-only requests; both motion and commissioning initialization; refusal and
control tick/torque invariants. Browser rendering exercises actual components.
Build reviewed ARM64, bind exact size/hash/source/API and known predecessor
updates, sign a new software version and validate old-client install/rollback.
Live hardware acceptance is separate and requires actual connected device state;
do not claim it based on emulators. Existing unpublished music work is excluded.
