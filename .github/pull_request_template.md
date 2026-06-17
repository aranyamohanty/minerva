## Description
Explain the changes you made, the technical rationale behind them, and how they address the issue.

## Linked Issues
Fixes #[issue_number]

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Refactor / Clean-up
- [ ] Documentation update

## Checklist
- [ ] My code follows the local-first principles of Minerva (no remote API dependencies).
- [ ] I have run `uv run pytest` and verified that all tests pass.
- [ ] I have run retrieval benchmarks (`uv run python tests/run_v5_benchmark.py`) and verified no regressions.
- [ ] I have added appropriate unit or E2E tests for my new changes.
- [ ] My changes do not introduce latency overhead to the hot paths (sub-15ms).
- [ ] I have updated the documentation / README accordingly.
