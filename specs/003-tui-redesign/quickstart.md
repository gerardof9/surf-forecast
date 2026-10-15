# Quickstart / manual validation — TUI redesign

**Feature**: `003-tui-redesign`  
**Branch**: `003-tui-redesign`  
**Mocks**: `mock2.png` (hierarchy reference); ignore `mock1.jpg` units/fields

## Prerequisites

- Python 3.12+ venv with project deps (`textual`)
- Presentation policies in `research.md` / `data-model.md` are confirmed (grade→score, bands, `PICOS DEL DÍA`, captions)

## Run TUI

```powershell
cd D:\repositorio\cursor\dev\surf-forecast
.\.venv\Scripts\python.exe -m surf_forecast
```

## Deterministic checks (pure Python)

After implementation, run the focused checks added for:

1. FR-017 label map
2. Grade → 1–5 whole-point score (confirmed ordinal table; no multi-factor formula)
3. Day rating uses only resolved peaks / best peak
4. Narrative omits unsupported claims when facts missing
5. Evolution sampling bands (incl. wind km/h pass-through when present)
6. Provisional-profile day and analysis-window-completed today
7. Existing engine fixture replay still succeeds

Exact commands will match whatever runner the tasks introduce (e.g. `python scripts/check_report_presentation.py`).

## Manual checklist — View A

- [ ] Title `SURF · LA PALOMA`; horizon today+4
- [ ] Data update time labeled distinctly from query time
- [ ] Focus starts on day list; ↑↓ changes day content
- [ ] `ANÁLISIS DEL DÍA` readable; scrolls; no silent clip
- [ ] Fact vs interpretation vs limitation visually distinguishable when both appear
- [ ] Stars match whole-point `n,n / 5` or `Sin valoración` + reason
- [ ] Section title exactly `PICOS DEL DÍA` — not “recomendados” / `SPOTS EVALUADOS`
- [ ] Cards ordered like engine ranking; best_of_day marker once; wind shows km/h when payload has pass-through
- [ ] Incomplete peak not shown as “Pocas olas”
- [ ] Narrow width: stacked, usable; wide: multi-panel OK
- [ ] Hierarchy recognizable vs `mock2.png` without copying mock numbers

## Manual checklist — View B

- [ ] Enter from card opens detail; Esc returns same day
- [ ] Sampled evolution rows only (documented bands); wind km/h when pass-through present
- [ ] Best window only if engine provides; else explicit absence
- [ ] Peak analysis present only with evidence; else omit/limitation
- [ ] Technical details **collapsed**; `D` expands with Hs vs derived, ages, snapshot
- [ ] No profiles screen (`p` gone); `o` stored-only still works
- [ ] Help documents keys and honesty (Hs ≠ beach face)

## Scenario matrix

| Scenario | Expect |
|----------|--------|
| Good resolved day | Day + peak ratings; analysis facts; best marker |
| Mixed peaks | Favorable day rating; poor cards stay poor |
| All uncertain/incomplete | `Sin valoración`; honest cards |
| Provisional profile | Limits visible; never “calibrated” |
| Today after 20:00 UYT | Analysis window completed; no new best window |
| Older data timestamp on later day | Labeled as data age/update, not false same-day refresh |

## Stop conditions

Do not ship if: engine fixtures regress; ratings invent scores for incomplete peaks; narrative invents cyclones/probabilities; technical pane is the default reading path; “recomendados” copy returns.
