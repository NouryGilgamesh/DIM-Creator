# DIM-Creator

*A fast PySide6 app for creating, packaging, and managing DAZ Install Manager (DIM) packages.*

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![PyQt5](https://img.shields.io/badge/GUI-PySide6-brightgreen)
![OS](https://img.shields.io/badge/OS-Windows-lightgrey)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-orange.svg)](LICENSE)
[![Total Downloads](https://img.shields.io/github/downloads/H1ghSyst3m/DIM-Creator/total)](https://github.com/H1ghSyst3m/DIM-Creator/releases)
[![Latest Release Downloads](https://img.shields.io/github/downloads/H1ghSyst3m/DIM-Creator/latest/total)](https://github.com/H1ghSyst3m/DIM-Creator/releases/latest)

**DIM-Creator** stages DAZ Studio content, generates the required DIM XML files, adds a cover image, and bundles everything into a ready-to-install DIM `.zip`—without the tedious manual setup.

---

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [System Requirements](#system-requirements)
- [Download & Install (EXE)](#download--install-exe)
- [Run from Source](#run-from-source)
- [Quick Start](#quick-start)
- [How Packaging Works](#how-packaging-works)
- [Workflows](#workflows)
- [Configuration & Data Paths](#configuration--data-paths)
- [Keyboard Shortcuts](#keyboard-shortcuts)
- [Troubleshooting](#troubleshooting)
- [Screenshots](#screenshots)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

### What is it?
A desktop app (PySide6 + qfluentwidgets) that builds **DAZ Install Manager (DIM)** packages.

### Who is it for?
DAZ Studio users, creators, and vendors who want fast, repeatable, and tidy DIM packages—with correct folder layout, a cover image, and the required XML manifests.

---

## Features

- **Make DIM packages in seconds** — just point to your files or an archive and click Generate.
- **Drag & drop file management** — organize your content without leaving the app.
- **Automatic folder detection** — files are placed where DIM expects them.
- **Cover art made easy** — drop an image and it’s formatted for DIM automatically.
- **Warnings before mistakes** — get notified about layout problems before packaging.
- **Store & tag presets** — save time with one-click product metadata.
- **Keeps your presets across updates** — your custom stores and tags won’t vanish after upgrading.
- **Works without Python** — available as a ready-to-run Windows `.exe`.

---

## System Requirements

- **OS:** Windows (officially supported)
- **Python:** 3.9+ (only needed when running from source)
- **External extractors** (for `.rar` / `.7z`):
  - **7-Zip** or **UnRAR** must be installed and available in your system `PATH`

> Tip: Installing [7-Zip](https://www.7-zip.org/) and enabling “Add to PATH” makes `.7z`/`.rar` imports work out of the box.

---

## Download & Install (EXE)

1. Download the latest release from **GitHub Releases**.
2. Unzip and run `DIMCreator.exe` — no Python environment required.

If SmartScreen warns about an unknown publisher, choose **More info → Run anyway**.

---

## Run from Source

```bash
git clone https://github.com/H1ghSyst3m/DIM-Creator.git
cd DIM-Creator
python -m venv .venv
. .venv/Scripts/activate  # Windows
pip install -r requirements.txt
python app.py
```

---

## Quick Start

1. Launch the app — your workspace is `Documents/DIMCreator/DIMBuild/Content`.
2. Pick your store, fill in product name/SKU, and (optional) add a cover image.
3. Add content by dragging it in or importing an archive.
4. Click **Generate** to create your DIM-ready `.zip`.

---

## How Packaging Works

- Your content folder becomes the installable DIM package.
- The app adds DIM’s required metadata files.
- A properly sized cover image is included.
- The result is a single, ready-to-install `.zip`.

---

## Workflows

### From a folder
1. Put your DAZ content into `DIMBuild/Content`.
2. Fill in details → Generate.

### From an archive
1. Import `.zip`, `.rar`, or `.7z`.
2. The app extracts only the correct DAZ folders.
3. Fill in details → Generate.

---

## Configuration & Data Paths

- **Workspace:** `Documents/DIMCreator/DIMBuild/Content`
- **Logs:** `Documents/DIMCreator/Logs`
- **Config Files:** `Documents/DIMCreator/Config/` (stores, tags, DAZ folder list)

Your custom settings and presets are preserved after updates.

---

## Keyboard Shortcuts

### Main window
- `Ctrl+G` — Generate GUID
- `Ctrl+Enter` — Generate DIM package
- `Ctrl+N` — Clear fields and clean workspace

### File Explorer
- `Ctrl+E` — Open in Explorer
- `Delete` — Delete selected item
- `Ctrl+C` / `Ctrl+X` / `Ctrl+V` — Copy / Cut / Paste
- `F2` — Rename
- `F5` — Refresh

---

## Troubleshooting

- **“.rar/.7z not extracting”** → Install **7-Zip** or **UnRAR** and add to `PATH`.
- **No DAZ folders found** → Content should start with folders like `data`, `People`, `Runtime`.
- **SmartScreen warning** → Allow the app via “More info → Run anyway”.

---

## Screenshots

<p align="center">
  <img width="781" height="721" alt="DIM-Creator main window" src="https://github.com/user-attachments/assets/3df3069e-211c-45e9-b3fa-51bc27bf31bb" />
</p>

---

## Contributing

Contributions are welcome!  
Open issues for bugs or ideas. PRs should use feature branches and focused commits.

---

## License

GNU GPL v3 — see [LICENSE](LICENSE).  
<sub>“DAZ” and “DAZ Install Manager” are trademarks of their respective owners. This project is not affiliated with or endorsed by DAZ 3D.</sub>
