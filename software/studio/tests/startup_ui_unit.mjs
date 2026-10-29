import { test } from 'node:test';
import assert from 'node:assert/strict';
import { existsSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const moduleUrl = new URL('../web/startup-status.js', import.meta.url);
const ui = existsSync(moduleUrl) ? await import(moduleUrl) : {};

test('the servo page and overview remain valid browser modules', () => {
  for (const path of ['../web/servo.js', '../web/app.js']) {
    assert.doesNotThrow(() => execFileSync(process.execPath, ['--check', fileURLToPath(new URL(path, import.meta.url))]));
  }
});

test('servo rows distinguish reply, latest miss and unknown evidence', () => {
  assert.equal(typeof ui.servoReplyStatus, 'function');
  assert.equal(ui.servoReplyStatus({ responding: true }).word, '有应答');
  assert.equal(ui.servoReplyStatus({ responding: false }).word, '未应答');
  assert.equal(ui.servoReplyStatus({ responding: null }).word, '未知');
  assert.equal(ui.servoReplyStatus({ responding: null }).kind, '');
  assert.equal(ui.servoReplyStatus({ fresh: false }), null, 'ordinary feedback keeps its existing rendering');
});

test('startup hero uses the backend wait reason and preserves the raw error', () => {
  assert.equal(typeof ui.startupStageCopy, 'function');
  const st = { posture: 'starting', start_wait: { text: '等待 IMU 数据（来源：lsm6dsv16x）' },
    start_error: 'Feetech host IMU has no sample', starting_long: true, starting_s: 40 };
  const copy = ui.startupStageCopy(st);
  assert.equal(copy.h, '等待 IMU 数据（来源：lsm6dsv16x）');
  assert.match(copy.sub, /Feetech host IMU has no sample/);
  assert.match(copy.sub, /40/);
  assert.equal(copy.act.href, '#/logs');
  assert.doesNotMatch(JSON.stringify(copy), /舵机没上电|可能其实起来了/);
});

test('generic waits stay generic, and old backend messages retain their existing fallback', () => {
  assert.equal(typeof ui.startupStageCopy, 'function');
  const copy = ui.startupStageCopy({ posture: 'starting', start_wait: { text: '等待总线设备响应' } });
  assert.equal(copy.h, '等待总线设备响应');
  assert.equal(ui.startupStageCopy({ posture: 'starting' }), null);
  assert.equal(ui.startupStageCopy({ posture: 'holding', start_wait: { text: 'old error' } }), null);
});
