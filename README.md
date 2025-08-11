# DIMCreator

DIMCreator is a PyQt5 desktop application for creating, packaging, and managing DAZ Install Manager (DIM) packages.  
It provides an intuitive GUI to prepare content, generate manifests, add product images, and zip everything into a ready-to-use DIM file.

---

## ✨ Features
- **Easy DIM Package Creation** – Generate `.zip` DIM-ready archives with manifests and supplements.
- **Drag & Drop Support** – Quickly add files or archives to your project.
- **Integrated File Explorer** – Browse, rename, copy, move, or delete files directly in the app.
- **Image Handling** – Add, preview, and process product images for DIM packages.
- **Content Validation** – Detect DAZ Studio content folder structure.
- **Archive Extraction** – Supports `.zip`, `.rar`, and `.7z` (requires 7-Zip/UnRAR installed).
- **Customizable Tags & Store Prefixes** – Quickly apply preset store IDs and tags.
- **Settings Panel** – Configure template archive copying and output paths.
- **Logging** – Detailed logs for troubleshooting.

---

## 🚀 Usage
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the application:
   ```bash
   python app.py
   ```
3. Workflow:
   - Select store and product information
   - Add product image (optional)
   - Drag & drop content or extract from an archive
   - Click **Generate** to create the DIM package

---

## 📜 License
This project is licensed under the **GNU General Public License v3.0** – see the [LICENSE](LICENSE) file for details.
