# Release Guide

## Local Release Check

```powershell
python -m pip install -e .[release]
python -m build
python -m twine check dist/*
```

## TestPyPI

If you want a safe dry run before the real publish:

```powershell
python -m twine upload --repository testpypi dist/*
```

## PyPI Publish

```powershell
python -m twine upload dist/*
```

## GitHub Publish Flow

This repository includes:
- `.github/workflows/ci.yml`
- `.github/workflows/publish-pypi.yml`
- `.github/workflows/release-assets.yml`

Recommended setup:
1. Create the GitHub repository.
2. Push this project to GitHub.
3. Use the PyPI project `pamm_ui`.
4. Configure PyPI trusted publishing for the GitHub repository.
5. Create a GitHub release.
6. Let the publish workflow upload the package to PyPI.
7. Let the release-assets workflow attach the built files to the GitHub release.

## Install From GitHub

Latest branch:

```powershell
pip install git+https://github.com/<your-user>/<your-repo>.git
```

Specific tag:

```powershell
pip install git+https://github.com/<your-user>/<your-repo>.git@v0.1.0
```

## Notes

- `publish-pypi.yml` uses trusted publishing, so it does not need a long-lived PyPI token once configured.
- If you prefer token upload, you can replace the publish step with a `TWINE_PASSWORD` secret flow.
