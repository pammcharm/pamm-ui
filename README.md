# PAMM UI

PAMM UI is a Python package and CLI for building desktop-style apps with `.htmlpy` and `.csspy` files, Python logic, and a native C rendering engine.

It gives you:
- a reusable Python library
- a `pamm` terminal command
- project scaffolding
- config-driven startup
- development autoreload
- formatting and VS Code setup helpers

## Install

### From PyPI
```powershell
pip install pamm_ui
```

After install:
```powershell
pamm --help
```

### Editable local install
```powershell
python -m pip install -e .
```

### From GitHub
Latest branch:

```powershell
pip install git+https://github.com/<your-user>/<your-repo>.git
```

Specific tag:

```powershell
pip install git+https://github.com/<your-user>/<your-repo>.git@v0.1.0
```

Download source as a zip from GitHub and install locally:

```powershell
pip install .
```

### Install release tools
```powershell
python -m pip install -e .[release]
```

## Use As A Package

You can import PAMM UI in any Python project after installation:

```python
from pamm_ui import Application, ProjectConfig, create_project, run_from_config

run_from_config("app.json", dev=True)
```

You can also run the package directly:

```powershell
python -m pamm_ui --help
python -m py_engine --help
```

## CLI Commands

### Create a project
```powershell
pamm create my_app
```

You can choose another target directory:

```powershell
pamm create my_app --dir D:\projects\my_app
```

You can also force autoreload on or off:

```powershell
pamm create my_app --autoreload yes
pamm create my_app --autoreload no
```

### Run a project
```powershell
pamm run my_app\app.json
```

Run in development mode:

```powershell
pamm run my_app\app.json --dev
```

### Development mode
```powershell
pamm dev my_app\app.json
```

### Doctor
Check installation and project health:

```powershell
pamm doctor
pamm doctor my_app\app.json
```

Try safe fixes too:

```powershell
pamm doctor my_app\app.json --fix
```

### Format
Format Python, `.htmlpy`, and `.csspy`:

```powershell
pamm format .
pamm format my_app
```

### Setup Dev
Write workspace settings for VS Code and optionally install helpful tools:

```powershell
pamm setup-dev .
pamm setup-dev my_app
pamm setup-dev my_app --install-python-tools
```

Skip extension installation if you only want workspace settings:

```powershell
pamm setup-dev my_app --no-extensions
```

## Project Structure

`pamm create` generates a project like this:

```text
my_app/
  app.json
  main.py
  README.md
  frontend/
    app_logic.py
    assets/
      app_icon.bmp
      showcase.bmp
    components/
      sidebar.htmlpy
    db/
      config.py
    layouts/
      shell.htmlpy
    pages/
      app.htmlpy
      home.htmlpy
    public/
    styles/
      app.csspy
      base.csspy
      theme.csspy
  backend/
    main.py
    services.py
  .vscode/
    launch.json
    settings.json
```

## Config File

PAMM UI apps are started from `app.json`.

Example:

```json
{
  "app_name": "my_app",
  "html": "frontend/pages/app.htmlpy",
  "css": [
    "frontend/styles/base.csspy",
    "frontend/styles/theme.csspy",
    "frontend/styles/app.csspy"
  ],
  "logic": [
    "main.py",
    "frontend/app_logic.py",
    "backend/main.py",
    "backend/services.py"
  ],
  "dll_path": null,
  "frontend_dir": "frontend",
  "backend_dir": "backend",
  "dev_mode": true,
  "autoreload": true,
  "watch": [
    "frontend",
    "backend",
    "main.py"
  ]
}
```

Important fields:
- `html`: main `.htmlpy` entry file
- `css`: one or more `.csspy` files
- `logic`: one or more Python files loaded by the app
- `dll_path`: optional override for a custom engine DLL path
- `autoreload`: reload changed content during development
- `watch`: files or folders watched in dev mode

## HTMLPY And CSSPY

`.htmlpy` files define structure:

```xml
<mainwin title="Dashboard">
    <cwin id="card1">
        <label text="Card 1" />
        <button text="Click Me" on_click="card1_click" />
    </cwin>
    <cwin id="card2">
        <label text="Card 2" />
        <button text="Click Me" on_click="card2_click" />
    </cwin>
</mainwin>
```

`.csspy` files define styles:

```css
mainwin {
    background: #0f1522;
}

.panel {
    background: #131d2f;
    border-radius: 28px;
}

button:hover {
    background: #476089;
}
```

## Generated Main Entry

Each generated project includes `main.py`, so a developer can also start the app with:

```powershell
python main.py
```

That file tries the installed package first and falls back to a nearby source checkout if needed.

## Editor Support

PAMM UI writes VS Code settings that:
- map `*.htmlpy` to HTML
- map `*.csspy` to CSS
- enable format-on-save
- enable Black for Python
- enable Ruff fixes and import cleanup

Recommended VS Code extensions:
- `ms-python.python`
- `ms-python.black-formatter`
- `charliermarsh.ruff`

## Library API

### Run from config
```python
from pamm_ui import run_from_config

run_from_config("app.json", dev=True)
```

### Create projects from code
```python
from pamm_ui import create_project

create_project("sample_app")
```

### Build your own app object
```python
from pamm_ui import Application, ProjectConfig

config = ProjectConfig.from_file("app.json")
app = Application()
app.load_project(config)
app.run()
```

## Cross-Project Usage

Once installed, PAMM is meant to work from any project folder, not only this repository.

Typical flow:
1. Install PAMM into your Python environment.
2. Run `pamm create my_app`.
3. Open the new project.
4. Run `pamm dev app.json`.
5. Edit `.htmlpy`, `.csspy`, and `.py` files.

## Publish To PyPI

PAMM UI is now set up to be packaged for PyPI and released from GitHub.

### Build locally
```powershell
python -m pip install -e .[release]
python -m build
python -m twine check dist/*
```

### Upload manually
```powershell
python -m twine upload dist/*
```

### GitHub Actions
This repo includes:
- `.github/workflows/ci.yml`
- `.github/workflows/publish-pypi.yml`
- `.github/workflows/release-assets.yml`

Recommended release flow:
1. Create a GitHub repository for PAMM UI.
2. Push this code to GitHub.
3. Create or publish the `pamm_ui` project on PyPI.
4. Configure PyPI trusted publishing for your GitHub repo.
5. Publish a GitHub release.
6. Let GitHub Actions build and upload the package.

Detailed release notes are in `RELEASE.md`.

## Notes

- The Python package is installable as `pamm_ui`.
- The importable helper modules are available through `pamm_ui.py` and `pamm.py`.
- The engine is still evolving, so some advanced widgets are scaffolded more than fully browser-grade today.
- The packaged install currently includes a Windows engine DLL.
- Linux and macOS support still need native engine packaging work before a full plug-and-play PyPI install is honest on those platforms.
- Live PyPI publishing still requires your PyPI account setup or trusted publishing configuration.
