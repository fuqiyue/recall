# Changelog

All notable changes to the Recall project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- GitHub Actions workflow for automated validation
- CHANGELOG.md for tracking project changes
- Comprehensive visual flow diagrams in `docs/RECALL_FLOW_DIAGRAMS.md`

## [0.2.0] - 2026-08-08

### Added
- Complete documentation overhaul
- GitHub repository metadata configuration guide (`.github-config.md`)
- 8 Mermaid flow diagrams for visualizing Recall workflows
- Enhanced README with clearer structure and examples

### Changed
- Restructured README.md for better accessibility
- Improved quick start guide with CLI examples
- Added Git vs Recall comparison table

### Fixed
- Clarified component architecture recording in documentation

## [0.1.0] - 2026-08-07

### Added
- Initial Recall system implementation
- Core CLI tool (`recall.bat` / `recall.sh`)
- Git integration for decision tracking
- Three-tier change channel system (simple/medium/high-risk)
- Documentation structure:
  - `logic_readme.md` - Current effective rules
  - `logic_change.md` - Active proposals
  - `logic_version/` - Historical records
- Python scripts for:
  - System initialization (`init_recall.py`)
  - Validation (`validator.py`)
  - Query operations (`query.py`)
  - Decision recording (`record.py`)
- Code Map feature for tracking component architecture

### Documentation
- Created `CLAUDE.md` with project instructions
- Created `docs/RECALL_FLOW_GUIDE.md` with workflow guide
- Added `logic_readme.md` template
- Added `logic_change.md` template

---

## Version Naming Convention

- **Major version (X.0.0)**: Fundamental changes to Recall philosophy or breaking changes
- **Minor version (0.X.0)**: New features, significant enhancements, documentation improvements
- **Patch version (0.0.X)**: Bug fixes, minor tweaks, typo corrections

[Unreleased]: https://github.com/fuqiyue/recall/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/fuqiyue/recall/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/fuqiyue/recall/releases/tag/v0.1.0
