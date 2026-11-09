# The Organizational Culture Assessment Toolbox (OCAI Toolbox)

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/Python-3.9%20%7C%203.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue.svg)](https://www.python.org/)
[![Engine: Polars](https://img.shields.io/badge/Engine-Polars%20v1.0%2B-orange.svg)](https://pola.rs/)

A high-performance statistical toolkit and computational engine developed in Python for advanced processing, hypothesis testing, and graphical visualization of survey data from the **Organizational Culture Assessment Instrument (OCAI)**.

The toolbox implements both traditional arithmetic scoring and advanced **Compositional Data Analysis (CoDA)** based on the methodology proposed by **Aitchison**, **Fossaluza (2012)**, and **van Eijnatten et al.**, utilizing Aitchison simplex geometry, vectorized block bootstrap confidence regions, and paired dimension-level permutation tests.

---

## 🚀 Key Highlights & Modern Engine (v2.0)

- **⚡ Ultra-High Performance with Polars**: Refactored from legacy single-threaded Pandas loops into a modern, multithreaded **Polars** engine in Rust. Execution time for 10,000 bootstrap resamples and 5,000 permutations dropped from **~40 minutes to under 4 seconds**, with RAM consumption dropping from **15 GB to under 100 MB**.
- **📦 Zero Heavy C-Dependencies**: Pure standalone CoDa zero-replacement engine (`multiReplace`), completely eliminating legacy compilation issues associated with `scikit-bio` on modern Python versions (fully compatible with Python 3.9 through Python 3.14+).
- **🏢 Hierarchical Sub-Group & Departmental Analysis**: Supports organization-wide analysis alongside nested departmental and sub-departmental evaluations (e.g., `["department", "subdepartment"]`), with native handling of homonymous sub-departments (e.g., `Engineering > Operations` vs. `Sales > Operations`) and configurable sample thresholds (`minGroupSize`).
- **☁️ Cloud & Headless Ready (AWS Lambda / REST APIs)**: `OcaiSummaryReport` replaces hardcoded console prints with pure, structured data objects supporting `.to_dict()` (JSON-serializable) for microservices and rich interactive HTML tables (`_repr_html_()`) in Jupyter Notebooks.
- **📊 Multi-Format Automated Export**: Single-command export to multi-sheet styled Excel workbooks (`.xlsx`), individual CSVs per department, and full JSON reports.
- **🎯 Competing Values Framework (CVF) Radars**: Standard Cameron & Quinn radar charts featuring 95% Bootstrap confidence interval shading and 2×3 dimensional panels.

---

## 📌 Theoretical Background

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

Because OCAI questions use a constant-sum (ipsative) scale totaling 100 points, the resulting data belongs to the **simplex** sample space (compositional data). The **OCAI Toolbox** employs **Compositional Data Analysis (CoDA)** techniques to preserve simplex geometry, avoid spurious negative correlations, and ensure scale-invariance.

---

## 🛠️ Architecture & Package Structure

```plaintext
OCAI_Toolbox/
├── ocai.py                               # Core high-performance engine & library (Polars + CoDa)
├── exampledb.csv                         # Sample hierarchical dataset (42 respondents, 6 sub-groups)
├── ocai_toolbox.ipynb                    # Modern executive Jupyter Notebook
├── Results/                              # Generated exports (Excel, CSVs, JSON)
├── legacy/                               # Historical desktop tools & scripts
│   ├── The Organizational Culture Assessment Toolbox.py  # Legacy Tkinter Desktop GUI (v1.0)
│   └── 2-instalar dependências.bat
└── README.md                             # Project documentation
```

---

## 💻 Quickstart Guide (Engine v2.0)

### 1. Installation

Install required lightweight dependencies:
```bash
pip install polars numpy matplotlib openpyxl
```

### 2. Basic Python Usage

```python
from ocai import OcaiAnalyzer
import matplotlib.pyplot as plt

# Initialize analyzer for overall organization
analyzer = OcaiAnalyzer(
    filePath="exampledb.csv",
    separator=";",
    numSamples=10000,   # Bootstrap resamples
    numPermut=5000,     # Permutations
    alpha=0.05          # Significance level (95% CI)
)

# Run full pipeline in seconds
analyzer.run()

# Display executive report
analyzer.summary()

# Plot CVF polar radar charts
analyzer.plotGlobal()
plt.show()

analyzer.plotDimensions()
plt.show()
```

### 3. Hierarchical Departmental Analysis

```python
analyzer = OcaiAnalyzer(
    filePath="exampledb.csv",
    separator=";",
    groupBy=["department", "subdepartment"],  # Composite hierarchical grouping
    minGroupSize=5,                            # Skip sub-groups with N < 5
    numSamples=10000,
    numPermut=5000,
    alpha=0.05
)
analyzer.run()

# 1. Benchmarking table across all departments
print(analyzer.getBenchmarkingTable())

# 2. Overlay sub-groups on a single radar chart
analyzer.plotSubGroupsComparison(state="Now")
plt.show()

# 3. Export all results to multi-sheet Excel, CSVs, and JSON
analyzer.exportToExcel("Results/ocai_complete_results.xlsx")
analyzer.exportToCsv("Results")
analyzer.exportToJson("Results/ocai_summary.json")
```

### 4. Headless Cloud & AWS Lambda Usage

`OcaiSummaryReport` produces pure JSON-serializable dictionaries without stdout dependencies:

```python
import json
from ocai import OcaiAnalyzer

def lambda_handler(event, context):
    analyzer = OcaiAnalyzer(
        filePath="/tmp/survey_input.csv",
        groupBy=["department", "subdepartment"],
        minGroupSize=5
    )
    analyzer.run()

    reportPayload = analyzer.summary().to_dict()

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(reportPayload)
    }
```

---

## 📊 Input Data Specification

### Modern CSV Format (`exampledb.csv`)
The input is a delimiter-separated text file (e.g. `;`) containing optional metadata columns to the left, followed by the **48 OCAI survey columns**:

| department *(opt)* | subdepartment *(opt)* | N-1-A | N-1-B | ... | P-6-D |
| :--- | :--- | :---: | :---: | :---: | :---: |
| Engineering | Backend | 25 | 25 | ... | 10 |
| Engineering | Operations | 20 | 30 | ... | 20 |
| Sales | Operations | 10 | 10 | ... | 35 |
| Human Resources | People | 50 | 20 | ... | 10 |

* **Naming Convention**: `{State}-{Dimension}-{Culture}`
  - State: `N` (Now), `P` (Preferred)
  - Dimension: `1`, `2`, `3`, `4`, `5`, `6`
  - Culture: `A` (Clan), `B` (Adhocracy), `C` (Market), `D` (Hierarchy)

---

## 📈 Methodological Workflow

```
┌────────────────────────────────────────────────────────────────────────┐
│ 1. Zero Imputation (multiReplace)                                      │
│    Replaces zeros with delta = 1/D^2 per question, preserving sum=100. │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ 2. Simplex Profile Calculations                                        │
│    Closed geometric mean in base 100 for CFP (Global) and CDP (Dims).  │
└───────────────────┬────────────────────────────────┬───────────────────┘
                    │                                │
                    ▼                                ▼
┌───────────────────────────────────────┐ ┌──────────────────────────────┐
│ 3. Bootstrap Confidence Intervals     │ │ 4. Paired Permutation Test   │
│    - Vectorized struct resampling     │ │    - Dimension-level paired  │
│    - Aitchison distance metric        │ │      swaps                   │
│    - Top alpha% outlier trimming      │ │    - Empirical p-values      │
│    - Simplex minimum and maximum      │ │    - Statistical decisions   │
└───────────────────────────────────────┘ └──────────────────────────────┘
```

---

## 📜 Legacy Desktop GUI (v1.0)

The original desktop version with Tkinter GUI is preserved in `legacy/The Organizational Culture Assessment Toolbox.py`. It provides a graphical interface built with Python 3.9 and Tkinter.

To run the legacy desktop GUI:
```bash
python "legacy/The Organizational Culture Assessment Toolbox.py"
```

---

## 📚 References & Theoretical Foundations

1. **Cameron, K. S., & Quinn, R. E. (2011)**. *Diagnosing and Changing Organizational Culture: Based on the Competing Values Framework*. Jossey-Bass.
2. **van Eijnatten, F. M., van der Ark, L. A., & Altena, R. (2015)**. *Compositional data analysis of the Organizational Culture Assessment Instrument*.
3. **Martin-Fernández, J. A., Barceló-Vidal, C., & Pawlowsky-Glahn, V. (2003)**. *Dealing With Zeros and Missing Values in Compositional Data Sets Using Nonparametric Imputation*. Mathematical Geology, 35(3), 253-278.
4. **Aitchison, J., & Egozcue, J. J. (2005)**. *Compositional data analysis: Where are we and where should we be going?*. Mathematical Geology, 37(7), 829-850.
5. **Fossaluza, V. (2012)**. *Análise de Dados Composicionais: Aplicações e Métodos*. Instituto de Matemática e Estatística, Universidade de São Paulo (USP).

---

## 👤 Author & License

- **Author**: Gabriel Gustavo Soares Santos
- **Institution**: University of São Paulo (USP)
- **License**: Released under the [GNU General Public License v3.0 (GPLv3)](LICENSE).
