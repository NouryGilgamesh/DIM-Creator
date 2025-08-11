# DIM-Creator

*A fast, cross-platform PyQt5 app for creating, packaging, and managing DAZ Install Manager (DIM) packages.*

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![PyQt5](https://img.shields.io/badge/GUI-PyQt5-brightgreen)
![OS](https://img.shields.io/badge/OS-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-orange.svg)](LICENSE)

DIM-Creator helps you prepare content, generate manifests, attach product imagery, and bundle everything into a ready-to-install DIM `.zip`—without wrestling with folder structures or manual XML.

---

## Table of Contents
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage Details](#usage-details)
- [Screenshots](#screenshots)
- [Contributing](#contributing)
- [License](#license)

---

## ✨ Features
- **One-click DIM Packages** — Build DIM-ready `.zip` archives with manifests and supplements.
- **Drag & Drop** — Add files or archives directly into your project.
- **Integrated File Explorer** — Browse, rename, copy, move, and delete inside the workspace.
- **Image Handling** — Add, preview, and process product images for DIM metadata.
- **Content Validation** — Detect and guide the DAZ Studio content folder layout.
- **Archive Extraction** — Import from `.zip`, `.rar`, and `.7z` (external tools required, see below).
- **Presets** — Apply store prefixes and tags with one click.

---

## ✅ Requirements
- **Python** 3.9 or newer
- **PyQt5** (installed via `requirements.txt`)
- **External extractors** (only needed if you import `.rar`/`.7z`):
  - **7-Zip** or **UnRAR** installed and available in your system `PATH`

> Tip: On Windows, installing [7-Zip](https://www.7-zip.org/) and checking “Add to PATH” simplifies `.7z`/`.rar` imports.

---

## 🛠 Installation
```bash
# 1) Clone the repository
git clone <your-repo-url>
cd DIM-Creator

# 2) Install dependencies
pip install -r requirements.txt
```

---

## 🚀 Quick Start
```bash
python app.py
```

1. Select your **store** and fill in **product info**.  
2. (Optional) Add a **product image**.  
3. Drag & drop a **content folder** or **import an archive** (`.zip`, `.rar`, `.7z`).  
4. Click **Generate** to create your DIM package.

The finished package `.zip` will appear in your configured **output path**.

---

## 📚 Usage Details
- **Stores & Tags**: Use presets to automatically prefix product IDs and apply tags.  
- **Images**: Drop in a cover image to include product art in your DIM metadata.  
- **Content Validation**: The app checks for standard DAZ content structure and will warn about common issues.  
- **Settings**: Configure template archive copying, output directories, and default behavior.  
- **Logs**: Open the log panel (or file) if something doesn’t work as expected.

---

## 📷 Screenshots

<img width="781" height="721" alt="DIM-Creator main window" src="https://github.com/user-attachments/assets/4d8c9832-72c0-48c0-87dc-4c4f3d0a8897" />

---

## 🤝 Contributing
Contributions are welcome!  
Feel free to open issues for bugs or enhancement ideas. For pull requests, please:
1. Create a feature branch.
2. Keep commits focused and well-described.
3. Add or update tests/docs when relevant.

---

## 📜 License
This project is licensed under the **GNU General Public License v3.0**.  
See the [LICENSE](LICENSE) file for full details.

<sub>“DAZ” and “DAZ Install Manager” are trademarks of their respective owners. This project is not affiliated with or endorsed by DAZ 3D.</sub>
