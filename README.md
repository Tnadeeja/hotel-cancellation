# Hotel Booking Cancellation Prediction

## Module

IT3051 – Fundamentals of Data Mining

Mini Project 2026

## Project Overview

**Approved project title:** AI-Based Hotel Booking Cancellation Risk Prediction Using Data Mining

This project applies a complete data-mining workflow to the Hotel Booking Demand dataset, using historical hotel reservation data to predict whether a booking is likely to be cancelled.

- **Target variable:** `is_canceled`
- **Task:** Binary classification
- **Classes:** `0` = Not Cancelled; `1` = Cancelled

## Business Problem

Unexpected booking cancellations can affect occupancy planning, room allocation, operational planning, and revenue management. The goal is to analyse historical reservation information and develop a cancellation-risk prediction solution that can support hotel planning.

## Refined Project Direction

The refined investigation is **Hotel-Type-Specific Cancellation Risk Prediction for City Hotel and Resort Hotel**. The dataset contains reservations from both hotel types, and the project will investigate whether their cancellation behaviour differs.

Later modelling will investigate:

- A general cancellation-prediction approach trained using both hotel types.
- City Hotel-specific modelling.
- Resort Hotel-specific modelling.

Whether hotel-specific models improve predictive performance is a hypothesis to be tested through later experiments, not an established result.

## Data Leakage Consideration

The project will investigate whether any dataset features directly reveal the cancellation outcome, become available only after relevant booking events, or would create unrealistic prediction performance. Feature availability will be assessed against a realistic prediction stage.

Leakage-related decisions will be documented during EDA and preprocessing. No final column-removal list has been established.

## Dataset

**Dataset name:** Hotel Booking Demand Dataset

**Original research source:** Antonio, N., Almeida, A., & Nunes, L.

The original dataset is publicly available. This project uses the CSV file `hotel_bookings.csv`.

The raw dataset is deliberately excluded from Git tracking. Each group member should place their local copy at:

```text
data/raw/hotel_bookings.csv
```

## Evaluation 1 Scope

The current project phase includes:

- Problem and dataset understanding.
- Dataset structure investigation.
- Exploratory data analysis.
- Data-quality investigation.
- Missing-value investigation.
- Duplicate investigation.
- Unusual-value/outlier investigation.
- Class-distribution investigation.
- City Hotel vs Resort Hotel analysis.
- Potential data-leakage investigation.
- Preprocessing.
- Feature engineering.
- Feature selection where appropriate.
- Preparation of training/testing data.

These activities define the planned Evaluation 1 scope; the repository is currently at the setup stage. Machine-learning model comparison belongs to the next project stage and is intentionally not part of the current implementation work.

## Repository Structure

```text
hotel-cancellation/
├── README.md
├── requirements.txt
├── .gitignore
├── data/
│   ├── raw/          # Local original dataset.
│   └── processed/    # Processed datasets generated later.
├── notebooks/        # Data understanding, EDA, and preprocessing notebooks.
├── src/              # Reusable Python code.
│   └── __init__.py
├── reports/
│   ├── figures/      # Generated EDA figures.
│   └── eval1/        # Evaluation 1 observations and preparation material.
└── docs/             # Project documentation including the data dictionary.
    └── data_dictionary.md
```

Local datasets and generated figures are ignored by Git; `.gitkeep` files preserve otherwise empty directories.

## Local Setup

Run these commands from the repository root.

Create a virtual environment:

```console
python -m venv .venv
```

Activate it in Command Prompt:

```bat
.venv\Scripts\activate
```

Or activate it in PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Install the requirements in the activated environment:

```console
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Place your local dataset copy at the path described above. When notebooks are added, open them using VS Code's Jupyter extension and select the `.venv` Python environment as the notebook kernel.

## Project Workflow

Planned workflow:

```text
Problem Understanding
→ Dataset Understanding
→ EDA
→ Data Quality Investigation
→ Leakage Investigation
→ Preprocessing
→ Feature Engineering
→ Model Development
→ Model Optimization
→ Final Prediction System
```

Later workflow stages have not yet been completed.

## Current Status

Evaluation 1 — Project Setup

