# ARK Pipeline Workspace — setup & cross-repo guide

You're reading this inside **`tk-config-swc`**, the Studio Wildcard ShotGrid / **Flow Production Tracking (FPT)**
pipeline config for *ARK*. The full pipeline is **not one repo** — it's this config plus a set of forked / custom
Toolkit repos that the config wires together. This file explains the whole workspace and **how to set it up from
scratch when all you have is this repo.**

- Config *internals* (env files, templates, schema, hooks): see **`CLAUDE.md`** (next to this file).
- This file is the canonical, shippable copy of the workspace guide. The dev machine also keeps an auto-loaded
  copy at `S:\Projects\ShotgunConfig\CLAUDE.md`; **edit this one** and keep that in sync.

---

## TL;DR — two ways to use the pipeline

- **Just run / test it (no fork editing):** the config pins almost everything via `app_store` / `git_branch` /
  `github_release`, which auto-download into the FPT bundle cache. You only need this repo + FPT Desktop 3.0 + the
  ShotGrid Pipeline Configuration pointed at it. You do **not** need to clone the sibling repos. ⚠️ One exception:
  any descriptor left in `type: dev` requires its repo cloned locally — see "No-dev rule" below.
- **Develop across the repos (full agent workspace):** clone the sibling repos next to this one and flip the
  components you're editing to `dev` mode. Follow **Bootstrap** below.

---

## Prerequisites

- **Flow Production Tracking Desktop 3.0** (ships the **Python 3.13** runtime + PySide6 / Qt 6.8). The whole pipeline
  targets this; older Desktop (Py 3.7) is not supported by the current config.
- **Git** + access to `github.com/StudioWildcard` (org membership / auth — `gh auth login` or a PAT with `repo`).
- **Windows x64** for the bundled Perforce binary: `tk-framework-perforce-swc` ships P4Python as per-Python-version
  `resources/p4python_pyXX_*` folders, and only **`p4python_py313_vc13_win64`** exists for FPT 3.0. macOS/Linux, or any
  other embedded Python version, need their own P4Python build added there (see that repo).

---

## Bootstrap: from *just `tk-config-swc`* → full dev workspace

### 0. Workspace path matters
The config's `dev` descriptors hardcode `S:/Projects/ShotgunConfig/<repo>`. For dev mode to work unmodified, the
workspace root **must be `S:\Projects\ShotgunConfig`**, with each repo a direct child:

```
S:\Projects\ShotgunConfig\
├─ tk-config-swc\                  ← this repo (branch sg_ark1_p4sg)
├─ tk-swc-perforce-sync\
├─ tk-multi-perforce\
├─ tk-framework-perforce-swc\
├─ tk-framework-qtwidgets\
├─ tk-swc-framework-shotgunutils\
├─ tk-multi-shotgunpanel\
└─ tk-framework-swc\
```
If you must use a different root, you'll have to edit the `dev` `path:` lines in `env/includes/*.yml` locally —
**don't commit those machine-specific paths.** (Or stay in live mode, which is path-independent.)

### 1. Place this repo correctly
Ensure this repo lives at `S:\Projects\ShotgunConfig\tk-config-swc` on branch `sg_ark1_p4sg`:
```powershell
# if you cloned it elsewhere, clone into the canonical location instead:
git clone -b sg_ark1_p4sg https://github.com/StudioWildcard/tk-config-swc.git S:\Projects\ShotgunConfig\tk-config-swc
```

### 2. Clone the sibling repos (only needed for dev work)
Each must be on its studio branch. PowerShell:
```powershell
$root = "S:\Projects\ShotgunConfig"
# repo -> branch
$repos = [ordered]@{
  "tk-swc-perforce-sync"          = "swc_main_ai"
  "tk-multi-perforce"             = "tester"
  "tk-framework-perforce-swc"     = "main"
  "tk-framework-qtwidgets"        = "swc_main_aei"
  "tk-swc-framework-shotgunutils" = "swc_main_ai"
  "tk-multi-shotgunpanel"         = "swc_main_aei"
}
foreach ($r in $repos.Keys) {
  git clone -b $repos[$r] "https://github.com/StudioWildcard/$r.git" "$root\$r"
}
# tag-pinned (detached HEAD is expected):
git clone https://github.com/StudioWildcard/tk-framework-swc.git "$root\tk-framework-swc"
git -C "$root\tk-framework-swc" checkout v1.4.5
```
bash equivalent: `git clone -b <branch> https://github.com/StudioWildcard/<repo>.git <repo>` for each row above.

### 3. Clean the Python environment (one-time, per machine)
FPT Desktop's embedded Python loads the user site-packages. A stale user-site `attrs` will shadow Desktop's bundled
copy and crash the web/browser-integration server (`cannot import name '__author__' from 'attr'`). Remove it:
```powershell
# run with the Python 3.13 that matches FPT Desktop's user-site
py -3.13 -m pip uninstall -y attrs
```

### 4. Point ShotGrid / FPT at this config
On the SG site, set the **ARK project's Pipeline Configuration** entity to use this config:
- **Dev (run the local working tree):** a path descriptor →
  `sgtk:descriptor:path?windows_path=S:\Projects\ShotgunConfig\tk-config-swc`
- **Live (pull from git):** a git descriptor →
  `sgtk:descriptor:git_branch?path=https://github.com/StudioWildcard/tk-config-swc.git&branch=sg_ark1_p4sg`

This is **ShotGrid-side** (the Pipeline Configuration entity) and is not managed from this repo.

### 5. Launch & verify
Launch FPT Desktop → open the *ARK* project. Confirm it boots, then that **P4SG** and **Perforce Status…** open and a
sync/publish works. If something fails, the log is `%APPDATA%\Shotgun\Logs\tk-desktop.log` — the gotchas table below maps
common symptoms to fixes.

### 6. (Optional) dev vs live switching
The config keeps each fork's inactive pin as `#LIVE#`-commented lines beside the active descriptor, so flipping
dev↔live is a comment swap. The **`dev-mode` / `live-mode`** Claude skills automate this across repos (and check out the
matching branches). **No-dev rule:** before committing/shipping the config, make sure **no descriptor is left in
`type: dev`** — run `grep -nE '^\s*type:\s*dev' env/includes/*.yml core/core_api.yml` (should be empty).

---

## Workspace map

| Repo | Working branch | Role / upstream it forks |
|------|----------------|--------------------------|
| **tk-config-swc** | `sg_ark1_p4sg` | This config (released `ark-v3.0.0`). |
| tk-swc-perforce-sync | `swc_main_ai` | **P4SG** main Perforce sync/publish app. SWC-original. |
| tk-multi-perforce | `tester` | Older Perforce app ("Perforce Status…", login-on-startup). SWC rewrite; upstream archived. |
| tk-framework-perforce-swc | `main` | Perforce framework — wraps **P4Python** (per-Python `P4API` binaries). Forks `shotgunsoftware/tk-framework-perforce` (heavily diverged). |
| tk-framework-qtwidgets | `swc_main_aei` | Fork of `shotgunsoftware/tk-framework-qtwidgets` (custom `context_selector`). |
| tk-swc-framework-shotgunutils | `swc_main_ai` | Fork of `shotgunsoftware/tk-framework-shotgunutils` (P4SG data layer). |
| tk-multi-shotgunpanel | `swc_main_aei` | Fork of `shotgunsoftware/tk-multi-shotgunpanel` (P4SG panel). |
| tk-framework-swc | tag `v1.4.5` | SWC-original utilities (context utils, SpeedTree `.SPM` thumbnails). |

**Resolved from the bundle cache (not cloned here):** tk-core (`app_store v0.23.8`), tk-desktop, tk-multi-loader2,
tk-multi-publish2, tk-multi-workfiles2, tk-shotgun-folders, tk-unreal, tk-copyfromplaylist, tk-unreal-launcher,
tk-substancepainter, tk-substancedesigner, tk-multi-snapshot, tk-framework-unrealqt, and all the `app_store`
engines/apps/frameworks. Their descriptors live in `env/includes/*.yml` and `core/core_api.yml`.

---

## Platform baseline (read before debugging "won't load" issues)

- Target: **FPT Desktop 3.0 = Python 3.13 + PySide6 / Qt 6.8**. Migration shipped as **`ark-v3.0.0`** (2026-05).
- **Known-good version matrix** = Autodesk's `shotgunsoftware/tk-config-default2` release **`v1.7.7`**. Match app_store
  versions to it. Core = **tk-core `v0.23.8`**.

### Python 3.13 / Qt 6 gotchas — symptom → cause → fix
| Symptom | Cause | Fix |
|---------|-------|-----|
| `No module named '…six.moves'` at startup | bundled `six` 1.13.0 `six.moves` loader dead on Py3.12+ | use a core off the new line; replace studio `from tank_vendor.six.moves import X` with stdlib (`urllib.request`, `queue`, …) |
| `cannot import name 'template' from 're'` | `re.template` removed in Py3.13 | delete the (usually unused) import |
| `ImportError … imp` | `imp` removed in Py3.12 | `importlib.util` |
| `distutils` import error | removed in Py3.12 | `packaging.version` |
| Dialog **silently never opens** | generated UI uses `QApplication.translate(…, QApplication.UnicodeUTF8)` — `UnicodeUTF8` gone in Qt6 | strip the dead 4th arg in `retranslateUi()` |
| Perforce apps fail: `Unable to locate a compatible version of P4Python for Python v3.13…` | per-Python P4Python binaries | add `resources/p4python_py313_vc13_win64/` (PyPI `p4python`) in tk-framework-perforce-swc |
| SSO browser login every launch / `cannot import name '__author__' from 'attr'` | P4AS OIDC ticket not reused; stale user-site `attrs` shadows bundled | ticket-gate `run_login`; `pip uninstall attrs` (Prereq §3) |

`QtGui.QSortFilterProxyModel`, `QLabel.setMargin`, `.exec_()`, and `hasattr(QtCore,'QString'/'QVariant')`-guarded code
are fine under the sgtk PySide6 shim.

---

## Conventions

- **Branches:** `sg_{project}_{feature}` (`sg_ark1_p4sg`, `sg_ark1_fpt3`); long-lived fork branches `swc_main_*`
  (`swc_main_ai`, `swc_main_aei`, `swc_main_flow`), plus repo-specific (`beta-ai`, `tester`, `main`).
- **Release tags:** `ark-v{major}.{minor}.{patch}` on `tk-config-swc` (current **`ark-v3.0.0`**). The `ark2-` prefix from
  a couple of 2026-03 releases is deprecated — use `ark-`. Cut with `gh release create … --draft`.
- **Commit trailer:** `Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`.
- **YAML:** 2-space indent; copyright header on `core/` files; strict parser.

## Shipping a fork fix (cross-repo)
1. Verify on Py3.13: `C:/Python313/python.exe -m py_compile <files>` (+ a live-app test).
2. Commit only the intended files to the fork's studio branch; `git push origin <branch>`; note the SHA.
3. In the config, flip that component `dev → git_branch` pinned to the new SHA (`live-mode` skill or edit YAML).
4. Enforce the **No-dev rule** + confirm YAML parses.
5. Commit + push `tk-config-swc`; cut/refresh the `ark-vX.Y.Z` release.

## Active work & deferred (as of ark-v3.0.0 — verify before relying on)
- **P4SG child-entity-exclusion** (tk-swc-perforce-sync `swc_main_ai`): skip child-entity sub-folders when syncing a
  parent. Sync side works; column-view filter + cache-hit prefix fix in test. Kept off `ark-v3.0.0` (which pins
  `sg_ark1_fpt3`, FPT3 fixes only). To ship: fold FPT3 into `swc_main_ai`, re-point config, cut `ark-v3.1.0`.
- **Deferred DCC engines (not yet Py3.13-migrated):** tk-substancepainter (`distutils`→`packaging`), tk-substancedesigner
  (fork + `imp`/PySide6), tk-unreal-launcher (PySide6 + hardcoded old core path), tk-framework-unrealqt (no Py3.13 build).

## Pointers
- Config internals: `CLAUDE.md` (this repo).
- Devlog: https://github.com/StudioWildcard/tk-config-swc/wiki/Devlog
