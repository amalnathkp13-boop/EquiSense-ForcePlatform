# PROJECT HANDOVER & SYSTEM SPECIFICATION: REVISION 2.0

**Project Name:** Low-Cost Four-Load-Cell Force Platform for Centre-of-Pressure (CoP) Assessment After Minor Lower-Limb Amputation  
**Working Title / Prototype:** EquiSense  
**Project Category:** Undergraduate Biomedical Engineering Capstone & Investigational Research Instrument  
**Institution:** Department of Biomedical Engineering, Tamil Nadu, India  
**Project Team:** Dhiyadharshini V., Kaviashree Rangasamy, Kameshwaran V., Lakshmi Praba M.  
**Supervisor:** Mrs. C. Radhika, AP/BME  
**Device Classification:** Non-certified investigational research instrument (Not a certified medical device; no conformity with IEC 60601-1 is claimed; not for autonomous clinical diagnosis).

---

## 1. Executive Summary & Problem Definition

### 1.1 Clinical Context
Quiet standing is governed by an active inverted-pendulum control loop driven by visual, vestibular, and somatosensory inputs. In patients with minor lower-limb amputations (toe, ray, or transmetatarsal amputations resulting from diabetes or Peripheral Arterial Disease [PAD]):
1. **The Actuator is Shortened:** Loss of the forefoot/toes shortens the antero-posterior lever arm through which the plantarflexor muscles apply corrective ankle moments, reducing the anterior Base of Support (BoS).
2. **The Sensor is Degraded:** Diabetic peripheral neuropathy attenuates plantar cutaneous and proprioceptive feedback loops.

This causes enlarged and faster corrective excursions (postural sway), leading to a high fall incidence. Conventional clinical scales (Berg Balance Scale, Timed Up and Go) are ordinal and subjective. Commercial research force plates (Kistler, AMTI) cost upwards of \$10,000 (₹8,00,000+), making them inaccessible for district-level rehabilitation centers in India.

### 1.2 System Mission
Provide a portable, low-cost (₹13,624 / ~$165 USD), battery-isolated 450 mm × 450 mm force platform that samples vertical ground reaction forces at **80 Hz**, measures Mean Velocity (**MVELO**) and the **95% Prediction Ellipse Area (PEA95)** with millimeter accuracy, and provides scientifically defensible balance metrics.

---

## 2. Revision 1 to Revision 2 Correction Register

This project underwent an exhaustive engineering overhaul (Revision 2.0) to eliminate specification errors present in early prototypes:

| ID | Parameter / Claim | Revision 1 (Flawed / Quarantined) | Revision 2.0 (Adopted & Verified) | Rationale & Engineering Physics |
|---|---|---|---|---|
| **2.1** | **Analogue Front-End** | Channel B, Gain 32 selected for "high headroom" | **Channel A, Gain 128** ($25$ clock pulses) | With $AVDD = 4.30\text{ V}$, a 200 kg cell at full scale outputs $8.60\text{ mV}$. Channel A ($128$) range is $\pm 16.80\text{ mV}$, retaining $1.95\times$ headroom over the full 200 kg rating. Gain 32 needlessly degrades the noise floor by $4\times$ and uses only $1.1\%$ of dynamic range for a 70 kg human. |
| **2.2** | **Sampling Rate** | Not stated; defaulted to $10\text{ Hz}$ on stock boards | **Hardware modified to $80\text{ Hz}$**; boot-rate enforced | $10\text{ Hz}$ grossly undersamples sway trajectory, artificially cutting MVELO in half (false stability). Pin 15 (RATE) must be tied to DVDD (Pin 16). Firmware blocks trials if $<60\text{ Hz}$. |
| **2.3** | **Synchronization** | Claimed "perfectly synchronized ADCs" | Declared worst-case inter-chip skew of **$12.5\text{ ms}$** | Shared `PD_SCK` clocks shift out data simultaneously, but internal RC oscillators free-run. At quiet stance sway speed ($10\text{ mm/s}$), artefact is $\le 0.13\text{ mm}$ (acceptable against $5\text{ mm}$ RMS target). |
| **2.4** | **Cross-Talk Physics** | Claimed Z-mount "eliminates lateral cross-talk" | Claim retracted; Z-mount **reduces mechanical constraint** | Bar load cells intrinsically respond to off-axis moments. Z-mount mitigates parasitic binding but does not isolate vertical shear. |
| **2.5** | **Static Indeterminacy**| Ignored | **Mandatory shimming** + uniform 8 N·m fastener torque | 4 supports on a rigid plane are statically indeterminate. Height differences $>0.2\text{ mm}$ create massive CoP bias that per-cell calibration cannot see. |
| **2.6** | **Measurement Domain** | Implied entire $450\times 450\text{ mm}$ plate | Restricted to **$400\times 400\text{ mm}$** sensor rectangle | CoP outside sensor perimeter is mathematical extrapolation. Firmware rejects CoP outside boundary with a 5 mm safety margin. |
| **2.7** | **Validation Standard**| Single-cell $R^2 > 0.999$ linearity | **9-Test Battery** including 25-point Grid Accuracy | Force linearity does not prove positional accuracy. Positional accuracy requires gain matching, true geometric spacing, and planar leveling. |
| **2.8** | **Sway Ellipse Type** | Unspecified "Sway Area" | **95% Prediction Ellipse Area (PEA95)** | Confidence ellipses shrink as $1/N$ (recording longer makes patient look artificially stable). Prediction ellipses remain asymptotically independent of $N$. |
| **2.9** | **AI / Classification**| Claimed arbitrary cutoffs ($3.0 / 7.0\text{ cm}^2$) as TinyML | **Baseline-referenced ratio** + Gated Logistic Regression | Hardcoded thresholds are not AI. Population cutoffs fail because amputee baselines vary. ML model ships disabled until trained on subject-disjoint data. |
| **2.10**| **Haptic Feedback** | Listed 5V motor with no trigger rule | **Rule specified ($2.5\times \text{RDIST}$)**; **Disabled for human trials** | Active vibration makes study "interventional" under CDSCO/MDR 2017, triggering clinical trial licensing. Disabled to maintain observational status. |

---

## 3. Hardware Architecture & Electrical Pinout

### 3.1 Hardware Components
* **Microcontroller:** ESP32-WROOM-32 / NodeMCU-32S (Dual-Core Xtensa LX6 @ 240 MHz).
* **Sensors:** 4× Phaeton 611E Parallel Beam Load Cells (Aluminum alloy, 200 kg capacity each, $2.0\text{ mV/V}$ sensitivity, IP65).
* **ADCs:** 4× HX711 24-bit Sigma-Delta breakout boards.
* **Power Source:** 2× 18650 Li-ion Battery Shield V8 (Provides galvanic isolation from 50 Hz AC mains, yielding a 25 dB noise floor reduction).

### 3.2 Pin Mapping (ESP32 NodeMCU)

```
ESP32 GPIO27 ──► PD_SCK of all 4 HX711 (shared clock)
ESP32 GPIO32 ◄── DOUT  FL      ESP32 GPIO33 ◄── DOUT  FR
ESP32 GPIO25 ◄── DOUT  BL      ESP32 GPIO26 ◄── DOUT  BR
ESP32 GPIO14 ──► Haptic PWM → AO3400A N-MOSFET (1N4007 flyback)
ESP32 GPIO2  ──► Status LED
```

| Signal Name | ESP32 GPIO | Direction | Notes / Constraints |
|---|---|---|---|
| **Shared `PD_SCK`** | **GPIO 27** | Output | Common clock to all 4 HX711 modules. |
| **`DT_FL` (Front-Left)** | **GPIO 32** | Input | Dedicated serial data line. |
| **`DT_FR` (Front-Right)**| **GPIO 33** | Input | Dedicated serial data line. |
| **`DT_BL` (Back-Left)** | **GPIO 25** | Input | Dedicated serial data line. |
| **`DT_BR` (Back-Right)**| **GPIO 26** | Input | Dedicated serial data line. |
| **`HAPTIC_PWM`** | **GPIO 14** | Output | PWM output through MOSFET driver (Disabled in clinical trial). |
| **Status LED** | **GPIO 2** | Output | On-board LED for self-test and error status. |

*Reserved / Avoided Pins:*
* `GPIO 6–11`: Connected internally to integrated SPI flash.
* `GPIO 12`: Strapping pin; high voltage during boot causes bootloader failure.
* `GPIO 16–17`: Connected to PSRAM on WROVER modules.
* `GPIO 34, 35, 36, 39`: Input-only pins (lack internal pull-up/pull-down and output drivers; cannot be used for clock lines).

### 3.3 Mandatory Hardware Hack: HX711 80 Hz Modification
Commercial green HX711 breakout boards ground Pin 15 (`RATE`) via a bottom PCB trace, locking the chip to 10 Hz.
1. Locate Pin 15 on the SOIC-16 HX711 package.
2. Cut the narrow PCB trace connecting Pin 15 to the ground plane using a precision scalpel.
3. Test continuity between Pin 15 and Ground to verify an open circuit.
4. Bridge a wire or solder jumper between Pin 15 (`RATE`) and Pin 16 (`DVDD`, 3.3 V).
   *Correction (Oct 2026): an earlier draft said Pin 6. Pin 6 is `VBG` (≈1.25 V reference) and is not a valid logic-high at DVDD = 3.3 V; use Pin 16.*
5. Verify on oscilloscope or via firmware boot self-test that reading interval is $\approx 12.5\text{ ms}$ ($80\text{ Hz}$).

### 3.4 Load Cell Wheatstone Bridge Connections (Channel A)
Each Phaeton 611E connects to its respective HX711 board:
* **Red Wire:** `E+` (Excitation Positive, $\approx 4.30\text{ V}$ derived from AVDD)
* **Black Wire:** `E-` (Excitation Ground)
* **Green Wire:** `A+` (Differential Signal Positive)
* **White Wire:** `A-` (Differential Signal Negative)
*(Note: Pins `B+` and `B-` are left disconnected).*

---

## 4. Mechanical Design & Geometric Constraints

                       FRONT (Anterior, +Y)
           X = -200 mm                       X = +200 mm
           Y = +200 mm                       Y = +200 mm
                 +-------------------------------+
                 | [FL]                     [FR] |
                 |   |                        |  |
                 |   <------- 400 mm -------->   |
                 |   |                        |  |
   LEFT (-X)     |   |         (0,0)          |   |     RIGHT (+X)
                 |   |        Origin          |  |
                 |   |                        |  |
                 |   <------- 400 mm -------->   |
                 |   |                        |  |
                 | [BL]                     [BR] |
                 +-------------------------------+
           X = -200 mm                       X = +200 mm
           Y = -200 mm                       Y = -200 mm
                        BACK (Posterior, -Y)
                 <------------- 450 mm ------------>


* **Plate Dimensions:** Outer envelope $450\text{ mm} \times 450\text{ mm} \times 6\text{ mm}$ (Tooling Plate Aluminum 6061-T6 preferred, or 12 mm marine plywood).
* **Sensor Coordinates:** Nominal center-to-center spacing is $400\text{ mm} \times 400\text{ mm}$.
  * $FL = (-200, +200)\text{ mm}$
  * $FR = (+200, +200)\text{ mm}$
  * $BL = (-200, -200)\text{ mm}$
  * $BR = (+200, -200)\text{ mm}$
* **Valid Measurement Domain:** Restricted strictly to $|X| \le 195\text{ mm}$ and $|Y| \le 195\text{ mm}$ ($400\text{ mm}$ square minus $5\text{ mm}$ boundary guard band).
* **Z-Mounting:** $3\text{ mm}$ ground steel spacers between load cell mounting bosses and plates to guarantee bar deflection without base contact. Fasteners torqued to $8\text{ N}\cdot\text{m}$.
* **Mechanical Safety Factor:** $4 \times 200\text{ kg} = 800\text{ kg}$ gross rating. For a maximum participant mass of $150\text{ kg}$, structural safety factor $> 5.3\times$.

---

## 5. Mathematical Formulations & Algorithms

### 5.1 Center of Pressure (CoP) General Form
Let $F_i$ be the vertical force reading from corner $i \in \{FL, FR, BL, BR\}$ and $(x_i, y_i)$ be its physical coordinates:

$$W_{total} = \sum_{i=1}^{4} F_i$$

$$X_{CoP} = \frac{\sum_{i=1}^{4} x_i \cdot F_i}{W_{total}} = \frac{200 \cdot [(F_{FR} + F_{BR}) - (F_{FL} + F_{BL})]}{F_{FL} + F_{FR} + F_{BL} + F_{BR}}$$

$$Y_{CoP} = \frac{\sum_{i=1}^{4} y_i \cdot F_i}{W_{total}} = \frac{200 \cdot [(F_{FL} + F_{FR}) - (F_{BL} + F_{BR})]}{F_{FL} + F_{FR} + F_{BL} + F_{BR}}$$

**Execution Guards Applied:**
1. *Negative Force Clamping:* If $F_i < 0.0$, clamp $F_i = 0.0$ to prevent corner unloading from driving CoP outside the physical boundaries.
2. *Threshold Gate:* Compute CoP if and only if $W_{total} \ge 20.0\text{ kg}$. Below $20\text{ kg}$, mark CoP invalid (`NaN`).
3. *Domain Boundary Check:* Reject sample if $|X_{CoP}| > 195\text{ mm}$ or $|Y_{CoP}| > 195\text{ mm}$.

### 5.2 Load Asymmetry Measures
* **Medio-Lateral Asymmetry:**  
  $$ASYM_{LR} = \frac{(F_{FR} + F_{BR}) - (F_{FL} + F_{BL})}{W_{total}} \times 100\%$$
* **Antero-Posterior Asymmetry:**  
  $$ASYM_{AP} = \frac{(F_{FL} + F_{FR}) - (F_{BL} + F_{BR})}{W_{total}} \times 100\%$$
  *(Negative $ASYM_{AP}$ indicates posterior/heel loading, characteristic of forefoot amputation).*

### 5.3 Posturographic Scatter & Dynamics (Prieto et al., 1996)
For a trial of $N$ valid samples collected at interval $\Delta t = 1/f_s$ ($T = N \cdot \Delta t$):
* Mean Centered Coordinates: $x[n] = X[n] - \bar{X}$, $y[n] = Y[n] - \bar{Y}$
* Radial Distance: $d[n] = \sqrt{x[n]^2 + y[n]^2}$
* **Total Excursion (Path Length):**
  $$TOTEX = \sum_{n=1}^{N-1} \sqrt{(X[n+1] - X[n])^2 + (Y[n+1] - Y[n])^2}$$
* **Mean Velocity (Primary Metric):**
  $$MVELO = \frac{TOTEX}{T}$$
* **RMS Distance:**
  $$RDIST = \sqrt{\frac{1}{N}\sum_{n=1}^{N} d[n]^2}$$

### 5.4 95% Prediction Ellipse Area (Schubert & Kirchner, 2014)
Do **not** use the confidence ellipse of the mean. The 95% Prediction Ellipse Area ($PEA_{95}$) is calculated via sample covariance matrix $S$:

$$S = \begin{bmatrix} s_x^2 & s_{xy} \\ s_{xy} & s_y^2 \end{bmatrix}$$

$$PEA_{95} = 2\pi \cdot F_{0.05}(2, N-2) \cdot \left[ \frac{(N+1)(N-1)}{N(N-2)} \right] \cdot \sqrt{\det(S)}$$

Where $F_{0.05}(2, m)$ with $m = N-2$ degrees of freedom is evaluated on the MCU via exact closed form:

$$F_{0.05}(2, m) = \frac{m}{2} \left[ 0.05^{-2/m} - 1 \right]$$

---

## 6. Firmware & Signal Processing Pipeline

### 6.1 RTOS Dual-Core Architecture
* **Core 1 (Real-Time Priority 3 Task):**
  * Blocks until all 4 data lines (`DT_FL`, `DT_FR`, `DT_BL`, `DT_BR`) transition low.
  * Enters an atomic critical section (`taskENTER_CRITICAL`) with interrupts disabled to pulse `PD_SCK` 25 times. (Preventing RTOS ticks from causing clock pulses $>60\ \mu\text{s}$, which triggers HX711 hardware power-down).
  * Executes second-order causal Butterworth low-pass filter.
  * Calculates CoP and evaluates real-time safety bounds.
* **Core 0 (Housekeeping & Telemetry Task):**
  * Handles JSON status server (`10 Hz`), serial CLI, Wi-Fi web dashboard, and baseline memory persistence in EEPROM/NVS.
  * Communicates with Core 1 via spinlock-protected shared memory buffers.

### 6.2 Digital Filtering Specifications
* **On-Device (Real-Time Causal):** 
  * 2nd-order Direct-Form II Transposed Butterworth low-pass filter.
  * $f_s = 80\text{ Hz}$, $f_c = 10\text{ Hz}$. Group delay $\approx 12\text{ ms}$.
  * Numerator coefficients $b = [0.097631, 0.195262, 0.097631]$
  * Denominator coefficients $a = [1.000000, -0.942809, 0.333333]$
  * *State Seeding:* Initial state initialized to steady-state value corresponding to $F[0]$ to prevent step-response transient swinging during trial startup.
* **Offline Processing (Official Metrics):**
  * 4th-order zero-phase forward-backward filter (`scipy.signal.filtfilt`, $f_c = 10\text{ Hz}$).
  * **All publication/report metrics must be derived from the offline zero-phase pipeline.**

---

## 7. Classification & Haptic Intervention Rules

### 7.1 Baseline-Referenced Rule (Active by Default)
1. Subject completes a 30-second quiet-stance baseline trial. Baseline $MVELO_{base}$ and $RDIST_{base}$ are stored.
2. Subsequent trials evaluate the ratio:
   $$Score = \frac{MVELO_{trial}}{MVELO_{base}}$$
3. Engineering Thresholds:
   * **Stable:** $Score < 1.5$
   * **Moderate Risk:** $1.5 \le Score < 2.5$
   * **High Fall Risk:** $Score \ge 2.5$

### 7.2 Trained Logistic Regression (Shipped Gated / Disabled)
The firmware contains code hooks for a 3-feature logistic regression classifier ($\mathbf{x} = [MVELO, PEA_{95}, ASYM_{AP}]$).
* **Status:** **Disabled.** Firmware returns `UNCALIBRATED` until trained on external clinical data.
* **Model Acceptance Gates:**
  * Minimum 40 independent trials across $\ge 8$ subjects.
  * Stratified Group k-Fold cross-validation (Subject-Disjoint: no subject appears in both train and test splits).
  * Model accuracy must beat majority-class baseline with statistical significance.

### 7.3 Haptic Biofeedback Rule
* **Dynamic Trigger Threshold:** $R_{thresh} = \max(6.0\text{ mm}, 2.5 \times RDIST_{base})$
* **PWM Drive:** Graded linearly from $R_{thresh}$ up to $45\text{ mm}$. Minimum pulse on-time $= 120\text{ ms}$, refractory blackout period $= 400\text{ ms}$ to eliminate mechanical bounce.
* **REGULATORY NOTE:** **Haptic feedback is physically disconnected and disabled in firmware during human observational trials** to comply with ICMR 2017 guidelines and prevent classification as an interventional clinical device under CDSCO MDR 2017.

---

## 8. Metrological Validation: The Nine-Test Battery

Before human trials, the assembled platform must pass these bench acceptance tests:

| Test ID | Test Name | Procedure | Acceptance Criteria |
|---|---|---|---|
| **V1** | **Sample Rate** | Measure duration of 80 hardware conversions | $\ge 60\text{ Hz}$ (Nominal $80\text{ Hz}$) |
| **V2** | **Noise Floor** | 400 unloaded samples after 60 min warm-up | RMS $< 20\text{ g}$ equivalent per cell |
| **V3** | **Per-Cell Linearity** | 0 to 100 kg load in 10 kg increments (up/down) | $R^2 > 0.999$, Hysteresis $< 0.5\%$ FS |
| **V4** | **Total Mass Accuracy**| Certified class $M_1$ mass at plate center | Error within $\pm 1\%$ of true load |
| **V5** | **Warm-up Drift** | 50 kg dead weight static logged for 30 min | Drift $< 0.5\%$ of reading |
| **V6** | **Grid Accuracy** | 20 kg compact weight placed across 25 lattice points | Radial RMS error $\le 5\text{ mm}$; Max $\le 10\text{ mm}$ |
| **V7** | **Repeatability** | V6 lattice repeated 3 times with re-placement | $\sigma \le 2\text{ mm}$ per point |
| **V8** | **CoP Noise** | 70 kg dead mass static load for 30 s | CoP RMS noise $< 1.0\text{ mm}$ |
| **V9** | **Cross-Talk** | Load one single corner; record opposite corners | Characterize off-axis parasitic coupling |

### 8.1 The 25-Point Grid Accuracy Procedure
Mark a $5 \times 5$ Cartesian grid on the top plate at $X, Y \in \{-150, -75, 0, +75, +150\}\text{ mm}$. Run an affine transform fit:

$$\begin{bmatrix} X_{true} \\ Y_{true} \end{bmatrix} = \begin{bmatrix} a_{11} & a_{12} \\ a_{21} & a_{22} \end{bmatrix} \begin{bmatrix} X_{meas} \\ Y_{meas} \end{bmatrix} + \begin{bmatrix} c_x \\ c_y \end{bmatrix}$$

* If post-fit residual collapses: Error is systematic (sensor spacing constant in firmware needs update).
* If post-fit residual remains $> 3\text{ mm}$: Error is non-linear mechanical binding (indicates warped plate or uneven shimming; cannot be calibrated out in software).

---

## 9. Bill of Materials (BOM) & Sourced Costs

| Component Description | Qty | Unit Cost (INR) | Extended Cost (INR) | Source / Notes |
|---|---|---|---|---|
| Phaeton 611E 200 kg Load Cell (2.0 mV/V) | 4 | ₹650 | ₹2,600 | Industrial weighing supplier |
| HX711 24-bit ADC Breakout Board | 4 | ₹120 | ₹480 | Generic green PCB |
| ESP32 NodeMCU-32S V1 Module | 1 | ₹450 | ₹450 | Espressif Systems clone |
| 6 mm Aluminum Top Plate ($450\times 450\text{ mm}$) | 1 | ₹1,800 | ₹1,800 | Local waterjet / machine shop |
| 12 mm Marine Plywood / Baseplate | 1 | ₹900 | ₹900 | Base support substrate |
| 3 mm Mild Steel Z-Mount Spacers & Shims | 8 | ₹90 | ₹720 | Laser cut & ground flat |
| M6 Grade 8.8 Fasteners, Nyloc Nuts, Washers | 16 | ₹12 | ₹192 | Fastener depot |
| Adjustable M8 Rubber Leveling Feet | 4 | ₹60 | ₹240 | Vibration damping base |
| 18650 Battery Shield V8 (Dual 3.7V cells) | 1 | ₹700 | ₹700 | Low-noise isolated power |
| 10 mm ERM Vibration Motor + MOSFET Driver | 1 | ₹165 | ₹165 | Haptic actuator circuitry |
| Enclosure, Cable Glands, 4-Core Loom | 1 | ₹600 | ₹600 | Shielded signal cabling |
| Calibration Mass Certified Service (5/10/20 kg) | 1 | ₹3,000 | ₹3,000 | Secondary reference standard |
| **Subtotal** | | | **₹11,847** | |
| **Contingency (15%)** | | | **₹1,777** | Mechanical rework / spare parts |
| **Total Build Cost** | | | **₹13,624** | **~$165 USD** (@ 82 INR/USD) |

---

## 10. Repository File Structure & Setup

```
EquiSense-ForcePlatform/
├── README.md
├── hardware/
│   ├── BOM.csv                         # Sourced bill of materials (Section 9)
│   ├── cad/                            # FreeCAD 1.1
│   │   ├── EquiSense_ForcePlatform.FCStd   # Parametric assembly (44 solids)
│   │   ├── EquiSense_ForcePlatform.step    # Neutral exchange format
│   │   ├── EquiSense_TopPlate_FEA_6mm.FCStd  # CalculiX FEA, 6 mm plate
│   │   ├── EquiSense_TopPlate_FEA_10mm.FCStd # CalculiX FEA, 10 mm option
│   │   └── renders/                    # Isometric, exploded, x-ray views
│   └── kicad/                          # KiCad 10
│       ├── EquiSense.kicad_pro / .kicad_sch
│       ├── EquiSense_ERC.rpt           # ERC: 0 errors, 0 warnings
│       ├── EquiSense.net               # Netlist
│       └── export/                     # Schematic PDF/SVG, BOM CSV
├── analysis/
│   ├── fea_6mm_nodes.csv               # Node results (x, y, z, von Mises, dz)
│   ├── plot_fea.py                     # Stress / deflection map script
│   └── fea_plot.png
├── docs/
│   ├── PROJECT_HANDOVER.md             # This specification
│   ├── Vishwakarma_Stage2_EquiSense.pptx
│   └── figures/
└── firmware/                           # ESP32 firmware (to be added in Month 2)
```

## 11. Quickstart Guide for Firmware Development

> Status: the `firmware/` and `tools/` folders are scheduled for Month 2 (Dec 2026). The steps below describe the intended workflow once they are committed.

### Step 1: Toolchain Installation
* Install **Arduino IDE 2.x** or **PlatformIO** (VS Code).
* Add ESP32 Board Package (v2.0.11 or later).
* Install dependencies: `HX711` by Bogdan Necula, `ArduinoJson`.

### Step 2: Verification of Hardware Rates
1. Flash `firmware/ForcePlatform/ForcePlatform.ino`.
2. Open Serial Monitor at **115200 baud**.
3. Send text command: `rate`.
4. Ensure the output reports: `Measured Rate: 80.xx Hz`.  
   *(If it reports $\approx 10\text{ Hz}$, stop. Pin 15 on the HX711 boards is not pulled high. Perform the hardware modification described in Section 3.3).*

### Step 3: Run Native Numerical Self-Tests
Verify the mathematics on your development PC before updating firmware:
```bash
cd tools
g++ -O3 selftest.cpp -o selftest
./selftest

```

Expected Output:
```

  - Prediction Ellipse Coverage (20,000 samples): 0.9500 [PASSED]
  - Filter DC Gain: 1.000000 [PASSED]
  - F-Distribution Critical Value m=2398: 2.9994 [PASSED]
```

### Step 4: Collect Real Data for the Machine Learning Model

To move the classifier out of its UNCALIBRATED state:

1.  Ensure the study protocol receives Institutional Ethics Committee (IEC)
    clearance under Framing B (Observational Research).
2.  Collect \ge 40 valid trials using the command: trial 30.
3.  Export CSV with dump.
4.  Run python tools/train_classifier.py --data trials.csv.
5.  The script will evaluate GroupKFold splits and generate model_weights.h only
    if the model beats the majority-class baseline.

## 12. Verified Scientific References

1.  Prieto, T. E., Myklebust, J. B., Hoffmann, R. G., Lovett, E. G., &
    Myklebust, B. M. (1996).
    Measures of postural steadiness: differences between healthy young and
    elderly adults.
    IEEE Transactions on Biomedical Engineering, 43(9), 956–966.
    DOI: 10.1109/10.532130
    (Establishes MVELO as the most sensitive posturographic parameter).
2.  Schubert, P., & Kirchner, M. (2014).
    Ellipse area calculations and their applicability in posturography.
    Gait & Posture, 39(1), 518–522. DOI: 10.1016/j.gaitpost.2013.09.001
    (Proves confidence ellipses are sample-size dependent; mandates prediction
    ellipses).
3.  Winter, D. A. (1995).
    A.B.C. (Anatomy, Biomechanics and Control) of Balance during Standing and
    Walking.
    Waterloo Biomechanics, Waterloo, Ontario, Canada.
    (Foundational text defining the relationship between ground reaction forces
    and CoP).

*End of Project Handover Document — EquiSense Rev 2.0, Department of Biomedical Engineering.*
