# tk-config-swc

Studio Wildcard's ShotGrid (Shotgun) Toolkit pipeline configuration for Ark game development.
Perforce-integrated, Unreal Engine-centric game asset pipeline.

## Architecture

- **Environment-driven**: 32+ env YAML files in `env/`, selected at runtime by `core/hooks/pick_environment.py`
- **YAML includes**: Modular config via `env/includes/` — centralized app, engine, and framework location descriptors
- **Asset hierarchy**: Supports parent/child assets, libraries, sections, categories, classes, and custom entity types (Campaigns, Production assets)
- **Path templates**: `core/templates.yml` (~1000 lines) defines all disk path patterns used by Toolkit
- **Folder schema**: `core/schema/` defines folder creation rules for projects, assets, shots, sequences
- **Storage root**: `core/roots.yml` — currently `primary` mapped to Z:\ ArkDepot (ShotGrid storage ID 135)
- **Custom hooks**: 53 Python hooks in `hooks/` across 7 subdirectories

## Supported DCCs

Maya, Houdini, 3ds Max, Photoshop, Substance Painter, Substance Designer, Unreal Engine

## Key Files

| File | Purpose |
|------|---------|
| `core/roots.yml` | Storage root definitions (maps to ShotGrid LocalStorage) |
| `core/templates.yml` | All path templates for file resolution |
| `core/hooks/pick_environment.py` | Environment selection logic — critical routing |
| `env/includes/app_locations.yml` | App version and location descriptors |
| `env/includes/engine_locations.yml` | Engine version and location descriptors |
| `env/includes/frameworks.yml` | Framework definitions and versions |
| `env/includes/settings/` | Per-engine and per-app settings (27 YAML files) |
| `hooks/` | Custom Python hooks (53 files, 7 subdirectories) |
| `info.yml` | Config metadata (min SG v7.2.0, min core v0.19.18) |
| `core/core_api.yml` | Toolkit core location (git_branch: swc_main) |

## Custom Forks (StudioWildcard GitHub)

| Component | Branch | Source |
|-----------|--------|--------|
| tk-core | swc_main | github.com/StudioWildcard/tk-core |
| tk-desktop | swc_main_aei | github.com/StudioWildcard/tk-desktop |
| tk-unreal | swc_main_aei | github.com/StudioWildcard/tk-unreal |
| tk-unreal-launcher | swc_main_aei | github.com/StudioWildcard/tk-unreal-launcher |
| tk-multi-workfiles2 | swc_main_flow | github.com/studiowildcard/tk-multi-workfiles2 |
| tk-multi-publish2 | beta-ai | github.com/StudioWildcard/tk-multi-publish2 |
| tk-multi-loader2 | swc_main_ai | github.com/studiowildcard/tk-multi-loader2 |
| tk-multi-shotgunpanel | swc_main_aei | github.com/StudioWildcard/tk-multi-shotgunpanel |
| tk-multi-perforce | tester | github.com/StudioWildcard/tk-multi-perforce |
| tk-swc-perforce-sync | swc_main_ai | github.com/StudioWildcard/tk-swc-perforce-sync |
| tk-shotgun-folders | swc_main_flow | github.com/studiowildcard/tk-shotgun-folders |
| tk-copyfromplaylist | swc-main | github.com/StudioWildcard/tk-copyfromplaylist |
| tk-framework-qtwidgets | swc_main_aei | github.com/StudioWildcard/tk-framework-qtwidgets |
| tk-framework-perforce-swc | main | github.com/StudioWildcard/tk-framework-perforce-swc |
| tk-swc-framework-shotgunutils | swc_main_ai | github.com/StudioWildcard/tk-swc-framework-shotgunutils |
| tk-framework-swc | v1.4.5 (tag) | github.com/StudioWildcard/tk-framework-swc |
| tk-substancepainter | master | github.com/studiowildcard/tk-substancepainter |
| tk-multi-snapshot | v0.8.1.2-swc | github.com/nimbleheroes/tk-multi-snapshot (release) |

## Development Conventions

- **Branch naming**: `sg_{project}_{feature}` (e.g., `sg_ark1_p4sg`)
- **Version tags**: `ark-v{major}.{minor}.{patch}` (current: `ark-v2.2.0`)
- **YAML style**: 2-space indent, Shotgun copyright header on core files
- **Commit messages**: Short descriptive phrases
- **CI**: `azure-pipelines.yml` (triggers on master, PRs, version tags)
- **Location descriptor types**: `app_store`, `git_branch`, `git`, `github_release`, `dev` (local)

## Common Tasks

- **Update an app version**: Edit `env/includes/app_locations.yml`, change version hash/tag
- **Update an engine**: Edit `env/includes/engine_locations.yml`
- **Update a framework**: Edit `env/includes/frameworks.yml`
- **Change environment routing**: Edit `core/hooks/pick_environment.py`
- **Add a new DCC context**: Create `env/{context}.yml`, update `pick_environment.py` to return it
- **Modify folder structure**: Edit files under `core/schema/`
- **Update path templates**: Edit `core/templates.yml`
- **Change storage root**: Edit `core/roots.yml` (see Guardrails below)

## Guardrails

- Do NOT change `shotgun_storage_id` in `roots.yml` without verifying the ShotGrid LocalStorage mapping via API
- Do NOT rename environment files without updating `core/hooks/pick_environment.py` references
- Do NOT alter YAML indentation style (2-space) — the Toolkit parser is strict
- Template paths in `templates.yml` map to real disk structures; changes affect file resolution across all DCCs
- Location descriptors (`git_branch`, `app_store`, `dev`) must point to valid, accessible sources
- Perforce hooks (`hooks/tk-multi-publish2/add_file.py`, `edit_file.py`, `delete_file.py`) interact with live P4 depots — test carefully
- The `@settings.<app>.<engine>.<env>` reference pattern in env files must match keys defined in `env/includes/settings/`

## Devlog

Wiki: https://github.com/StudioWildcard/tk-config-swc/wiki/Devlog
