# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## v1.1.0
### Added

### Changed

### Fixed


## v1.0.0 - 2025-08-12
### Added
- Initial public release of **DIM-Creator**.
- Windows build pipeline using PyInstaller.
- Automated GitHub Actions workflow for:
  - Building EXE files on Windows.
  - Packaging versioned release ZIP with README and LICENSE included.
  - Uploading artifacts for CI runs.
  - Attaching raw EXE and ZIP files to GitHub Releases for tagged versions.
- Bundled all necessary assets into the executable for easy distribution.

### Changed
- Optimized startup time by preloading UI components.
- Improved asset packaging to ensure all files are included in the release.