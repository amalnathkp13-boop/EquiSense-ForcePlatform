# EquiSense: Four-Load-Cell Force Platform

A low-cost, battery-isolated 450 × 450 mm force platform that measures Centre-of-Pressure (CoP) sway at 80 Hz. It is built for balance assessment after minor lower-limb amputation (toe, ray, transmetatarsal) in district-level rehabilitation centres.

**Team:** Dhiyadharshini V. · Kaviashree Rangasamy · Kameshwaran V. · Lakshmi Praba M.
**Supervisor:** Mrs. C. Radhika, AP/BME, Department of Biomedical Engineering
**Programme:** Vishwakarma Awards 2026-27, Stage 2

> Investigational research instrument. It is not a certified medical device, no IEC 60601-1 conformity is claimed, and it is not intended for autonomous clinical diagnosis.

## Key specifications (Rev 2.0)

| Parameter | Target |
|---|---|
| Sampling | 80 Hz per channel, 4 × HX711 (Channel A, gain 128), shared PD_SCK |
| Sensors | 4 × Phaeton 611E, 200 kg, 2.0 mV/V, at (±200, ±200) mm |
| CoP accuracy | ≤ 5 mm RMS, ≤ 10 mm max (25-point grid test) |
| CoP noise | < 1.0 mm RMS (70 kg static) |
| Metrics | MVELO (primary), RDIST, PEA95 prediction ellipse, ASYM_AP / ASYM_LR |
| Controller | ESP32-WROOM-32 (NodeMCU-32S), dual-core |
| Power | 2 × 18650 shield, no mains connection |
| Build cost | ₹13,624 (see `hardware/BOM.csv`) |

## Repository contents

| Path | What it is |
|---|---|
| `hardware/cad/EquiSense_ForcePlatform.FCStd` / `.step` | FreeCAD 1.1 assembly: top plate with 25-point test grid, 4 load cells, Z-mount spacers, M6 hardware, base, levelling feet, enclosure |
| `hardware/cad/EquiSense_TopPlate_FEA_6mm.FCStd`, `_10mm.FCStd` | CalculiX linear-static FEA of the top plate (2 × 150 kg on two foot pads) |
| `hardware/cad/renders/` | Isometric, exploded and x-ray renders |
| `hardware/kicad/` | KiCad 10 schematic (ESP32 + 4 HX711 channels + power + haptic driver), ERC report, netlist, BOM, PDF/SVG export |
| `hardware/BOM.csv` | Sourced bill of materials |
| `analysis/` | FEA node results and the plotting script `plot_fea.py` |
| `docs/PROJECT_HANDOVER.md` | Full Rev 2.0 system specification: maths, firmware design, validation battery |
| `docs/Vishwakarma_Stage2_EquiSense.pptx` | Stage 2 submission deck |
| `firmware/` | ESP32 firmware, scheduled for Month 2 (Dec 2026) |

## FEA summary (top plate, 2 × 150 kg = 2,943 N)

| Result | 6 mm Al 6061-T6 | 10 mm option |
|---|---|---|
| Max deflection | 2.56 mm | 0.61 mm |
| Field stress (> 40 mm from supports) | 56 MPa (FoS 4.9) | 21 MPa (FoS 13) |
| Peak at spacer edge (geometric singularity) | 276 MPa | 120 MPa |

Mesh: Gmsh 2nd-order tetrahedra, about 56,500 nodes.

## Important hardware note: HX711 80 Hz modification

Cut the trace that grounds **Pin 15 (RATE)** and tie it to **Pin 16 (DVDD, 3.3 V)**. Do **not** use Pin 6: that is VBG (≈1.25 V), which is not a valid logic-high. Check the result with the boot rate test (target ≈ 12.5 ms between samples).

## Opening the files

- CAD: FreeCAD 1.1 or newer (`.FCStd`), or any CAD tool via `.step`.
- Schematic: KiCad 10 (`hardware/kicad/EquiSense.kicad_pro`). The symbols are embedded in the schematic.
- FEA plot: `cd analysis && python plot_fea.py`

## Validation plan

Bench battery V1–V9 (rate, noise, linearity, mass accuracy, drift, 25-point grid accuracy, repeatability, CoP noise, cross-talk) runs before any human data is collected. Human data collection starts only after Institutional Ethics Committee clearance under the ICMR 2017 guidelines (observational design).

## References

1. Prieto TE et al. Measures of postural steadiness. *IEEE Trans Biomed Eng* 1996;43(9):956–966.
2. Schubert P, Kirchner M. Ellipse area calculations and their applicability in posturography. *Gait & Posture* 2014;39(1):518–522.
3. Wong CK, Chihuri ST, Li G. Risk of fall-related injury in people with lower limb amputations. *J Rehabil Med* 2016;48:80–85.
4. Viswanathan V, Kumpatla S. Pattern and causes of amputation in diabetic patients: a multicentric study from India. *JAPI* 2011;59:148–151.
