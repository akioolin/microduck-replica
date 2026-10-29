"""Independent ID 200 evidence must never establish control or calibration readiness."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE.parent), str(HERE.parent / "deps"), str(HERE.parent / "dev")]

from studio.imu import ImuBackend, bus_imu_of, calibration_context, mount_of
from studio.robotd import Robotd
from studio.rpc import Timeout
from studio.state import summarize
from tests.test_startup_status import QuietLog, startup_bus


def diagnostic(**changes):
    return dict({"source": "bus", "attempted": True, "responding": True, "age_ms": 10,
                 "info": {"protocol": "feetech", "board": "imu_to_dxl", "identity": [1, 2, 3],
                          "profile": "legacy"}, "sample_valid": True, "sensor_ready": True,
                 "sample_fresh": None, "sequence": 1, "error": None}, **changes)


class ImuDiagnosticTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.rd = Robotd("none", "none", QuietLog())
        self.rd.present = True
        bus = startup_bus(error="Feetech torque state failed; missing IDs [21]")
        bus["native"].update(imu_source="bus", configured_imu_profile="legacy",
                             imu_observation=diagnostic(), imu_mount_verified=False)
        self.rd.bus.set(bus)
        self.rd.bus.at = 100.
        self.backend = ImuBackend(self.rd, QuietLog(), self.tmp.name, root=self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def obs(self):
        return self.rd.bus.value["native"]["imu_observation"]

    def view(self, now=100.2):
        with mock.patch("studio.imu.time.monotonic", return_value=now):
            view = self.backend.view()
        self.assertIsInstance(view.get("diagnostic"), dict, "missing independent diagnostic view")
        return view

    def summary(self, now=100.2):
        result = summarize(self.rd, {}, now=now)
        self.assertIsInstance(result["imu"].get("diagnostic"), dict, "missing independent overview diagnostic")
        return result

    def test_only_imu_and_partial_servos_report_independently_in_both_modes(self):
        for mode in ("motion", "commissioning"):
            self.rd.bus.value["mode"] = mode
            rows = self.rd.bus.value["native"]["servo_observations"]["rows"]
            for online in (0, 4, 15):
                for i, row in enumerate(rows):
                    row["responding"] = i < online
                st, view = self.summary(), self.view()
                with self.subTest(mode=mode, online=online):
                    self.assertEqual(st["servos"]["online"], online)
                    self.assertEqual(st["imu"]["diagnostic"]["status"], "identified")
                    self.assertEqual(view["diagnostic"], st["imu"]["diagnostic"])
                    self.assertEqual(view["diagnostic"]["info"]["board"], "imu_to_dxl")
                    self.assertFalse(view["ready"])
                    self.assertEqual(st["posture"], "starting")
                    self.assertFalse(st["guard"])
                    self.assertIsNone(st["gravity"])
                    self.assertIsNone(view["imu_bus"], "diagnostic identity is not calibration context")
                    json.dumps(view, allow_nan=False)

    def test_response_data_wait_no_response_stale_and_unknown_are_distinct(self):
        for change, expected in (({"sample_valid": False}, "data_wait"),
                                 ({"sensor_ready": False}, "data_wait"),
                                 ({"responding": False, "info": None}, "no_response"),
                                 ({"sample_fresh": False}, "stale"),
                                 ({"info": None, "error": "identity unknown"}, "unknown"),
                                 ({"attempted": False}, "unknown")):
            self.rd.bus.value["native"]["imu_observation"] = diagnostic(**change)
            with self.subTest(change=change):
                self.assertEqual(self.view()["diagnostic"]["status"], expected)

    def test_identified_board_survives_unknown_sample_flags_and_dxl2_has_no_ready_flag(self):
        for changes, expected in (({"sample_valid": None, "sensor_ready": None}, "data_wait"),
                                  ({"sample_valid": True, "sensor_ready": None,
                                    "info": {"protocol": "dxl2", "board": "sflp_124_12",
                                             "profile": "legacy", "identity": [1, 2, 3]}}, "identified")):
            self.rd.bus.value["native"]["imu_observation"] = diagnostic(**changes)
            with self.subTest(changes=changes):
                d = self.view()["diagnostic"]
                self.assertEqual(d["status"], expected)
                self.assertIs(d["responding"], True)
                self.assertIsNotNone(d["info"])
                self.assertFalse(self.view()["ready"])

    def test_wire_age_and_studio_receipt_age_are_added_at_three_second_boundary(self):
        self.obs()["age_ms"] = 2800
        self.assertEqual(self.view(100.199)["diagnostic"]["status"], "identified")
        for now in (100.2, 100.201):
            d = self.view(now)["diagnostic"]
            self.assertEqual(d["status"], "stale")
            self.assertIsNone(d["info"])
            self.assertIsNone(d["responding"])
        self.rd.bus.at = 100.2
        self.obs()["age_ms"] = 3000
        self.assertEqual(self.view()["diagnostic"]["status"], "stale", "new RPC cannot renew frozen native data")

    def test_absent_failed_or_new_daemon_invalidates_cached_evidence(self):
        for present, error, hello_at in ((False, None, None), (None, None, None),
                                         (True, "transport failed", None), (True, None, 100.1)):
            self.rd.present, self.rd.bus.error, self.rd.hello.at = present, error, hello_at
            with self.subTest(present=present, error=error, hello_at=hello_at):
                d = self.view()["diagnostic"]
                self.assertEqual(d["status"], "unknown")
                self.assertIsNone(d["info"])
                self.assertEqual(self.summary()["imu"]["diagnostic"], d)

    def test_unknown_old_or_malformed_fields_never_guess_healthy(self):
        original = diagnostic()
        for change in (None, {}, {"age_ms": None}, {"age_ms": True}, {"age_ms": float("nan")},
                       {"responding": 1}, {"sample_valid": "true"}, {"sensor_ready": 1},
                       {"source": "lsm6dsv16x"}, {"info": {"protocol": "future", "board": "ft6"}}):
            self.rd.bus.value["native"]["imu_observation"] = (
                None if change is None else {} if not change else dict(original, **change))
            with self.subTest(change=change):
                d = self.view()["diagnostic"]
                self.assertEqual(d["status"], "unknown")
                json.dumps(d, allow_nan=False)
        del self.rd.bus.value["native"]["imu_observation"]
        self.assertEqual(self.view()["diagnostic"]["status"], "unknown")

    def test_source_or_configured_profile_change_cannot_reuse_bus_identity(self):
        for source, profile in (("lsm6dsv16x", "legacy"), ("bus", "qinmo"), ("bus", "future")):
            self.rd.bus.value["native"].update(imu_source=source, configured_imu_profile=profile)
            with self.subTest(source=source, profile=profile):
                d = self.view()["diagnostic"]
                self.assertEqual(d["status"], "unknown")
                self.assertIsNone(d["info"])
                self.assertEqual(self.summary()["imu"].get("source"), source)

    def test_conflicting_top_level_profile_invalidates_diagnostic_identity(self):
        self.rd.bus.value["configured_imu_profile"] = "qinmo"
        d = self.view()["diagnostic"]
        self.assertEqual(d["status"], "unknown")
        self.assertIsNone(d["info"])

    def test_startup_legacy_metadata_cannot_become_current_board_or_mount_binding(self):
        bus = self.rd.bus.value
        bus["native"]["imu_bus"] = copy.deepcopy(self.obs()["info"])
        calib = {"imu_source": "bus", "calibration": {"imu_mount_quat": [1, 0, 0, 0],
                  "imu_mount_verified": True, "imu_bus_profile": "legacy"}}
        self.assertIsNone(bus_imu_of(bus))
        self.assertFalse(mount_of(bus, calib)[1]["verified"])
        before = calibration_context(bus, "bus", {})
        self.obs()["info"]["identity"] = [9]
        self.obs()["age_ms"] = 9000
        self.assertEqual(calibration_context(bus, "bus", {}), before)

    def test_diagnostic_response_never_overwrites_native_control_or_pose(self):
        bus = self.rd.bus.value
        bus.update(mode="commissioning", torque_state="off")
        self.rd.health.set({"imu": {"ready": False}})
        self.rd.health.at = 100.
        self.assertEqual(self.summary()["imu"]["status"], "missing")
        self.assertFalse(self.view()["ready"])
        self.assertIsNone(self.view()["gravity"])
        self.assertFalse(bus["native"]["imu_mount_verified"])
        self.assertIsNone(self.backend.last_result)

    def test_new_daemon_or_failed_bus_cannot_project_old_control_metadata(self):
        bus = self.rd.bus.value
        bus["phase"] = "control"
        bus["native"].update(imu_bus=copy.deepcopy(self.obs()["info"]), imu_ready=True)
        self.rd.calib.set({"imu_source": "bus", "imu_mount": {"quat": [1, 0, 0, 0], "verified": True}})
        self.rd.calib.at = 100.
        self.assertEqual(self.view()["imu_bus"]["board"], "imu_to_dxl")
        self.backend.last_result = {"ok": True}
        for error, hello_at, now in (("poll transport failed", None, 100.2),
                                      (None, 100.1, 100.2), (None, None, 103.)):
            self.rd.bus.error, self.rd.hello.at = error, hello_at
            with self.subTest(error=error, hello_at=hello_at, now=now):
                view = self.view(now)
                self.assertIsNone(view["imu_bus"])
                self.assertIsNone(view["source"])
                self.assertIsNone(view["mount"])
                self.assertIsNone(self.backend.last_result)
                self.assertIs(bus["native"]["imu_ready"], True, "raw native control cache is preserved")
                self.assertFalse(self.summary(now)["imu"].get("context_current", True))


class ImuDiagnosticTransportTest(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.rd = Robotd("none", "none", QuietLog())

    async def test_bus_query_failure_marks_cached_evidence_invalid(self):
        self.rd.bus.set({"native": {"imu_observation": diagnostic()}})
        async def call(*args, **kw):
            raise Timeout("bus timeout")
        self.rd.poll.call = call
        await self.rd._ask("bus", "robot.busStatus")
        self.assertIn("bus timeout", self.rd.bus.error or "")

    async def test_other_poll_transport_failure_also_invalidates_cached_evidence(self):
        self.rd.bus.set({"native": {"imu_observation": diagnostic()}})
        async def call(*args, **kw):
            raise Timeout("poll transport timeout")
        self.rd.poll.call = call
        await self.rd._ask("health", "robot.health")
        self.assertIn("poll transport timeout", self.rd.bus.error or "")


if __name__ == "__main__":
    unittest.main()
