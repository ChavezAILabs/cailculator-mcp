# Golden Test Suite

Fixed inputs with known expected outputs. The suite is the safety net for every release
and for the MCP 2.0 migration, which must pass it unchanged.

```
pytest tests/golden -q
```

That one command runs every case twice:

1. **in-process**, calling the tool handler directly;
2. **at the MCP level**, through `python -m cailculator_mcp.server` spawned over stdio
   from a throwaway temp directory. That is a hostile working directory, the pattern
   from AIEX-499, where the `illustrate` asset-path bug only reproduced this way.

It then checks the two runs produce identical output, and prints a pass/fail table
with the suite version (`VERSION`) and commit.

Runtime is about 15–25 minutes. `analyze_dataset` and `chavez_transform` take ~35 s per
call because of the `hypercomplex` library's multiplication speed. Set
`GOLDEN_MCP_WORKERS` (default 2) to change how many servers run in parallel.

## Two kinds of golden, labeled differently

| `verification` | Meaning | What a pass shows |
|---|---|---|
| `hand` | Expected value derived by hand, independently of CAILculator | **correctness** |
| `lean` | Expected value proved in Lean (file and theorem named in `source`) | **correctness** |
| `literature` | Expected value from a published theorem or record | **correctness** |
| `recorded` | Captured from the current code and reviewed | only **no regression**; it cannot show the code was ever right |

Never present a `recorded` pass as a correctness proof. Today the only correctness golden
is `cd16_s1_lean*` (`lean/BilateralCollapse.lean`, `Pattern1_CD4`). The Tier 1 64D pair
is `recorded` until Paul confirms which pattern he verified by hand; the notes on
`cd64_zd_negative_signflip` include the 2√2 derivation so it can be upgraded.

## Case file

`cases/<id>.json`; the file name must equal `id`.

| Key | Required | Meaning |
|---|---|---|
| `id`, `tool`, `args` | yes | What to call. `{"$data": "file.json"}` loads `data/file.json`; `{"$float": "nan"}` / `"inf"` inject non-JSON floats. |
| `verification`, `source` | yes | See the table above; `source` names the reference. |
| `expected` | | Nested subset of the response. Only listed keys are compared: booleans and strings exactly, numbers within `tolerance` (default 1e-12). Unlisted and volatile fields (timestamps) are ignored. |
| `tolerance` | | `{"dotted.path": abs_tol}`. Recorded floats get 1e-9·\|v\|. |
| `expected_input_hash` | | Pinned `provenance.input_hash`. Catches silent changes to input normalization. |
| `expected_structural_findings` | | For `analyze_dataset`: the list of positive structural findings (see `runner.structural_findings`). Null controls expect `[]`. |
| `profile`, `null_control` | | Used by the profile gate check (G2): which profile the case exercises, and whether it is a null control. |
| `agreement_group` | | Cases asking the same question of different tools; their verdicts must agree. |
| `known_failure` | | `{"reason": ...}`. The case records the *correct* expectation, but the code does not meet it yet. It reports XFAIL (visible, does not block), and XPASS fails the run so the marker gets removed. It counts as failing for the profile gates. |
| `record_keys` | | Dotted paths `record_case.py` copies into `expected`. |
| `notes` | | Anything a reviewer needs. |

Every response must also carry a `provenance` block with all required keys, the right
`tool`, and, for profile cases, the profile's name, version and tier.

## Adding a case

1. Write `cases/<id>.json` with `id`, `tool`, `args`, `verification`, `source`, `notes`.
2. Hand, Lean or literature cases: write `expected` yourself from the independent
   derivation, then pin the hash with `python tests/golden/record_case.py --hash-only <id>`.
3. Recorded cases: list `record_keys`, then run `python tests/golden/record_case.py <id>`,
   and **read the recorded values** before committing.
4. Inputs larger than a few numbers go in `data/`. `data/generate_data.py` shows how the
   committed datasets were made (seeded).

## Change policy

- A golden's expected value (or pinned input hash) may change **only** with a CHANGELOG
  entry stating the reason. `record_case.py --force` exists for that case and nothing else.
- **Never regenerate goldens in bulk to make a failing run pass.**
- If a `hand`, `lean` or `literature` golden fails, the code is presumed wrong until
  shown otherwise.
- Removing a `known_failure` marker, or changing a case's `verification`, also needs a
  CHANGELOG line.
- Bump `VERSION` whenever cases are added, removed or changed. The version is stamped
  into every release build and reported as `provenance.golden_suite`.

## Release gate

`python scripts/release_gate.py` must pass before `python -m build` / `twine upload` and
before `railway up`. It runs this suite, checks that every profile's gate record is
current, and only then stamps and builds. See `docs/RELEASE_CHECKLIST.md`.
