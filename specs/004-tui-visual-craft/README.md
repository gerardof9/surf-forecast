# 004 — TUI visual craft

Professional graphic layer for Surf Forecast (LazyGit / btop / K9s quality bar).

**Active Spec Kit feature** (`.specify/feature.json`): `specs/004-tui-visual-craft`

| Document | Role |
|----------|------|
| **[`graphic-layer.md`](./graphic-layer.md)** | Binding visual / component contract |
| [`spec.md`](./spec.md) | Feature spec + clarifications FR-G11–G15 |
| [`plan.md`](./plan.md) | Implementation plan (`/speckit-plan`) |
| [`research.md`](./research.md) | Technical decisions |
| [`data-model.md`](./data-model.md) | Display view-models |
| [`quickstart.md`](./quickstart.md) | Manual + smoke validation |
| [`contracts/`](./contracts/) | Chrome + hygiene contracts |
| [`tasks.md`](./tasks.md) | Implementation tasks (`/speckit-tasks`) |
| [`references/`](./references/) | `modelo.png` + non-compliant baselines |

**Status (2026-10-15)**: Graphic layer implemented under `src/surf_forecast/presentation/tui/` (`formatters`, `theme`, `components/*`). Smoke: `scripts/check_tui_visual_smoke.py`. Manual VS-* screenshot gates remain operator sign-off per `quickstart.md`.
