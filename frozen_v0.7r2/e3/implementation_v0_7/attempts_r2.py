from __future__ import annotations

import re
from dataclasses import dataclass, field

E3A_ID = re.compile(r"^E3A-OFFICIAL-ATTEMPT-[0-9]{3}$")
E3B_ID = re.compile(r"^E3B-F([1-4])-OFFICIAL-ATTEMPT-[0-9]{3}$")


class InfrastructureFailure(RuntimeError):
    def __init__(self, subtype, message=""):
        super().__init__(message or subtype)
        self.subtype = subtype


def validate_attempt_id(attempt_id, phase, family=None):
    if phase == "A":
        return bool(E3A_ID.fullmatch(attempt_id))
    if phase == "B":
        match = E3B_ID.fullmatch(attempt_id)
        return bool(match) and family == f"F{match.group(1)}"
    raise ValueError("phase must be A or B")


@dataclass
class AttemptRecord:
    attempt_id: str
    manifest_name: str
    expected_episode_n: int
    status: str = "RUNNING"
    invalidation_reason: str | None = None
    episode_records: list = field(default_factory=list)
    attempted_scenario_ids: set = field(default_factory=set)

    def begin_episode(self, scenario_id):
        if scenario_id in self.attempted_scenario_ids:
            raise InfrastructureFailure(
                "RUNNER_EXCEPTION",
                f"duplicate episode attempt prohibited: {scenario_id}",
            )
        self.attempted_scenario_ids.add(scenario_id)

    def append_episode(self, record):
        self.episode_records.append(record)

    def invalidate(self, subtype):
        self.status = "INVALID_INFRASTRUCTURE"
        self.invalidation_reason = subtype

    def complete(self):
        if len(self.attempted_scenario_ids) != self.expected_episode_n:
            raise InfrastructureFailure(
                "RUNNER_EXCEPTION",
                "VALID requires every frozen manifest row attempted exactly once",
            )
        if len(self.episode_records) != self.expected_episode_n:
            raise InfrastructureFailure(
                "RUNNER_EXCEPTION",
                "VALID requires one episode record per frozen manifest row",
            )
        self.status = "VALID"
