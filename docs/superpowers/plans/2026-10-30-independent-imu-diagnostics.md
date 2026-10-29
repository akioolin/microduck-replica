# Independent IMU implementation and software release

- [x] Trace the startup gate, web state mapping and signed updater baseline.
- [x] Record approved diagnostic-only design and stable wire contract.
- [x] Native regression RED, bounded diagnostic implementation, both startup modes,
  frozen-RPC aging and safety regression GREEN; IPC42/build.47; review.
- [x] Web regression RED, freshness/context-safe overview and IMU diagnostic UI,
  browser checks and surrounding regression GREEN; review.
- [x] Build exact frozen ARM64 artifact and synchronize managed native updater,
  supported .44/.45/.46 predecessors and clean terminal journal handling.
- [x] Run final stable full Studio/updater suites and focused native baseline
  comparison; document pre-existing failures rather than weakening checks.
- [x] Push reviewed source, freeze/sign software2026.10.30, assemble bootstrap,
  verify original engine install/rollback/crash recovery and every attachment.
- [x] Publish GitHub software release, retain image Latest, verify anonymous old
  client discovery/download/signatures and record final evidence.

The prior user authorization covers implementing independent diagnostics and
including it in the normal software update. No physical movement or image reflash
is required for software work. Preserve existing worktrees and personal configs.
