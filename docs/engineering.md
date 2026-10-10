# Engineering and CI Baseline

This project uses a minimal, reproducible engineering baseline designed for a local-first research prototype.

## Quality gates

- `make install` installs the backend Python dependencies.
- `make install-frontend` installs the Vite React frontend dependencies.
- `make test` runs the repository test suite.
- `make frontend-build` runs the frontend production build.
- `make ci` runs the standard repo validation path.

## CI workflow

The GitHub Actions workflow in `.github/workflows/ci.yml` runs:

1. backend dependency installation
2. backend pytest suite
3. frontend dependency installation
4. frontend production build

This workflow is intentionally conservative: it validates the local-first stack without requiring API credentials or external services.

## Operational guidance

- Keep dataset files local and do not commit generated artifacts unless intentionally versioned.
- Treat retrieval metrics and safety outputs as research artifacts, not clinical evidence.
- Preserve the principle that the project remains local-first and privacy-aware by default.
