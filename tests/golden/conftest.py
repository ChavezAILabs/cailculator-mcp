"""
Session plumbing for the golden suite: a small pool of spawned MCP servers
(each launched from its own temp directory, the AIEX-499 hostile-cwd pattern),
a result cache shared by all tests, and the pass/fail table printed at the end.
"""

import os
from concurrent.futures import Future, ThreadPoolExecutor
from typing import Dict, Tuple

import pytest

from runner import MCPServer, git_commit, load_cases, run_inprocess, suite_version

CASES = load_cases()
CASES_BY_ID = {c["id"]: c for c in CASES}
MCP_WORKERS = int(os.environ.get("GOLDEN_MCP_WORKERS", "2"))

# (case_id, mode) -> "PASS" / "FAIL" / "XFAIL" / "XPASS"
OUTCOMES: Dict[Tuple[str, str], str] = {}


class ResultCache:
    """Runs each case once per mode; MCP runs start at session begin, in parallel."""

    def __init__(self):
        self._inprocess: Dict[str, dict] = {}
        self._mcp: Dict[str, Future] = {}
        self.servers = []
        self.pool = None

    def start_mcp(self):
        self.servers = [MCPServer() for _ in range(MCP_WORKERS)]
        self.pool = ThreadPoolExecutor(max_workers=len(self.servers))
        for i, case in enumerate(CASES):
            server = self.servers[i % len(self.servers)]
            self._mcp[case["id"]] = self.pool.submit(
                server.call_tool, case["tool"], case["resolved_args"])

    def inprocess(self, case_id: str) -> dict:
        if case_id not in self._inprocess:
            case = CASES_BY_ID[case_id]
            self._inprocess[case_id] = run_inprocess(case["tool"], case["resolved_args"])
        return self._inprocess[case_id]

    def mcp(self, case_id: str) -> dict:
        return self._mcp[case_id].result(timeout=3600)

    def close(self):
        if self.pool:
            self.pool.shutdown(wait=True, cancel_futures=True)
        for s in self.servers:
            s.close()


@pytest.fixture(scope="session")
def results():
    cache = ResultCache()
    cache.start_mcp()
    yield cache
    cache.close()


def pytest_report_header(config):
    return f"golden suite v{suite_version()} | commit {git_commit()} | {len(CASES)} cases"


def pytest_terminal_summary(terminalreporter):
    if not OUTCOMES:
        return
    tr = terminalreporter
    ids = sorted({cid for cid, _ in OUTCOMES})
    width = max(len(i) for i in ids)
    tr.section(f"golden suite v{suite_version()} @ {git_commit()}")
    tr.write_line(f"{'case'.ljust(width)}  {'verification':12}  in-process  mcp (temp cwd)")
    for cid in ids:
        ver = CASES_BY_ID[cid]["verification"] if cid in CASES_BY_ID else "-"
        tr.write_line(f"{cid.ljust(width)}  {ver:12}  "
                      f"{OUTCOMES.get((cid, 'inprocess'), '-'):10}  {OUTCOMES.get((cid, 'mcp'), '-')}")
    counts = {}
    for v in OUTCOMES.values():
        counts[v] = counts.get(v, 0) + 1
    tr.write_line("totals: " + ", ".join(f"{k} {v}" for k, v in sorted(counts.items())))
