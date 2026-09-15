# The Organizational Culture Assessment Toolbox (OCAI Toolbox)

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE)

A desktop application and statistical toolkit developed in Python for advanced processing, hypothesis testing, and graphical visualization of survey data from the **Organizational Culture Assessment Instrument (OCAI)**.

The toolbox implements both traditional arithmetic scoring and advanced **Compositional Data Analysis (CoDA)** based on the methodology proposed by **van Eijnatten et al.**, utilizing Aitchison geometry, bootstrap confidence intervals, and permutation tests to evaluate cultural profiles and their evolution over time.

---

## 📌 Project Overview

The **Organizational Culture Assessment Instrument (OCAI)**, developed by Kim Cameron and Robert Quinn based on the **Competing Values Framework (CVF)**, evaluates organizational culture across six key dimensions:
1. Dominant Characteristics
2. Organizational Leadership
3. Management of Employees
4. Organization Glue
5. Strategic Emphases
6. Criteria of Success

Respondents divide 100 points among four organizational culture archetypes for each dimension, both for the current state (**Now**) and the desired state (**Preferred**):
- **A — Clan (Collaborate)**: Focus on human development, teamwork, and employee empowerment.
- **B — Adhocracy (Create)**: Focus on innovation, flexibility, agility, and risk-taking.
- **C — Market (Compete)**: Focus on competitiveness, goal achievement, and market leadership.
- **D — Hierarchy (Control)**: Focus on stability, standardized procedures, and predictability.

Because OCAI questions use a constant-sum (ipsative) scale totaling 100 points, the resulting data belongs to the **simplex** sample space (compositional data). Traditional arithmetic means can introduce distortions and spurious negative correlations. The **OCAI Toolbox** addresses this limitation by offering **Compositional Data Analysis (CoDA)** techniques alongside standard arithmetic analysis.

---

## ✨ Key Features

### 1. Multi-Method Profile Calculations
- **Arithmetic Collective Full Profile (CFP)**: Computes traditional arithmetic averages across all respondents and dimensions.
- **Geometric Collective Full Profile (CFP)**: Computes the closed geometric mean profile following compositional data principles.
- **Zero-Replacement Preprocessing**: Employs multiplicative replacement (`scikit-bio`) to handle zero-value responses without distorting geometric mean calculations.

### 2. Statistical Robustness & Confidence Intervals
- **Non-Parametric Bootstrap Resampling**: Simulates resampled populations across user-defined iterations (default: 5,000 to 100,000 resamples).
- **Aitchison Distance Filtering**: Calculates Aitchison distances between resampled profiles and the central geometric profile, filtering out extreme distances ($\alpha$-cutoff) to generate robust non-parametric confidence intervals.

### 3. Hypothesis Testing (Permutation Tests)
- **Current vs. Preferred Culture**: Permutation testing to assess whether the difference between current ("Now") and desired ("Preferred") cultural states is statistically significant ($H_0$ equality vs. $H_1$ difference).
- **Longitudinal Cultural Evolution**:
  - **Past Culture vs. Current Culture**: Evaluates whether an organization's culture has significantly changed across two evaluation periods.
  - **Previously Preferred vs. Current Culture**: Evaluates whether current culture has successfully converged toward what was previously desired.

### 4. Radar / Polar Visualizations
Generates high-resolution polar radar charts with customizable options:
- Single-state profiles (Now or Preferred, Arithmetic or Geometric).
- Comparative overlays: Current vs. Preferred (Arithmetic or Geometric).
- Method comparison: Arithmetic vs. Geometric profiles.
- Confidence interval boundaries: Geometric profile bounded by lower and upper confidence limit polygons.
- Optional transparent background for seamless export into presentations and reports.

### 5. Automated Export
- Structured Excel spreadsheets (`.xlsx`) containing CFP profiles, intermediate transformations, and confidence limits.
- Text reports (`.txt`) detailing permutation test outputs ($p$-values, significance thresholds, and execution times).
- High-DPI radar charts exported directly to the output folder.

---

## 🛠️ Architecture & Technologies

- **Language**: Python 3.9 (Legacy environment)
- **GUI Framework**: Tkinter
- **Data Manipulation**: `pandas`, `numpy`, `openpyxl`
- **Scientific & Statistical Computing**: `scipy`, `skbio.stats.composition` (`scikit-bio`)
- **Plotting & Visualization**: `matplotlib` (polar projection engine)

---

## 📊 Input Data Format

The application expects an Excel spreadsheet (`.xlsx`) with a **3-level hierarchical MultiIndex header**:

| Level | Name | Valid Values | Description |
|---|---|---|---|
| **Level 0** | State | `Now`, `Preferred` | Evaluation state (current vs. preferred) |
| **Level 1** | Dimension | `1`, `2`, `3`, `4`, `5`, `6` | The 6 OCAI survey dimensions |
| **Level 2** | Culture | `A`, `B`, `C`, `D` | The 4 culture types (Clan, Adhocracy, Market, Hierarchy) |

Each subsequent row represents an individual respondent's answers. An example dataset structured according to this specification is provided in `Base semi aleatória.xlsx`.

> [!IMPORTANT]
> The number of respondents must match across the evaluated states, and the multi-level headers must strictly follow this structure.

---

## 🚀 Installation & Running

> [!NOTE]
> **Legacy Notice**: This project is built for **Python 3.9**. Modern Python versions (Python 3.10+) may encounter dependency or build incompatibilities with older releases of `scikit-bio` and associated C-extensions. It is recommended to run this project inside a Python 3.9 virtual environment.

### Step 1: Clone the Repository
```bash
git clone https://github.com/gbrielgustavo/OCAI_Toolbox.git
cd OCAI_Toolbox
```

### Step 2: Set Up Environment & Install Dependencies

#### Option A: Using a Python 3.9 virtual environment (Recommended)
```bash
# Create and activate a Python 3.9 virtual environment
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
# source venv/bin/activate

# Install required dependencies
pip install numpy pandas openpyxl scipy matplotlib scikit-bio
```

#### Option B: Windows batch script (Legacy)
Run `2-instalar dependências.bat` as Administrator on a machine with Python 3.9 installed.

### Step 3: Run the Application
Ensure that the output directories `Resultados/` and `Gráficos/` exist in the working directory, then start the GUI:
```bash
python "The Organizational Culture Assessment Toolbox.py"
```

---

## 📂 Repository Contents

```plaintext
├── The Organizational Culture Assessment Toolbox.py  # Main application (GUI + Calculation engine)
├── Base semi aleatória.xlsx                          # Sample dataset for testing
├── Manual.pdf                                        # Portuguese user guide and manual
├── 2-instalar dependências.bat                       # Legacy Windows dependency installer script
├── Beta Release.zip                                  # Standalone packaged beta release
└── LICENSE                                           # GNU General Public License v3.0
```

---

## 📚 References & Theoretical Foundations

1. **Cameron, K. S., & Quinn, R. E. (2011)**. *Diagnosing and Changing Organizational Culture: Based on the Competing Values Framework*. Jossey-Bass.
2. **van Eijnatten, F. M., van der Ark, L. A., & Altena, R.** (2015). *Compositional data analysis of the Organizational Culture Assessment Instrument*.
3. **Aitchison, J., & Egozcue, J. J. (2005)**. *Compositional data analysis: Where are we and where should we be going?*. Mathematical Geology, 37(7), 829-850.
4. **Fossaluza, V. (2012)**. *Análise de Dados Composicionais: Aplicações e Métodos*. Instituto de Matemática e Estatística, Universidade de São Paulo (USP).

---

## 👤 Author & License

- **Author**: Gabriel Gustavo Soares Santos
- **Institution**: University of São Paulo (USP)
- **License**: Released under the [GNU General Public License v3.0 (GPLv3)](LICENSE).
