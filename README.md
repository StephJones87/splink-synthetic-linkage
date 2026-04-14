# 🧩 Synthetic Data Linkage with Splink

## Overview

This project demonstrates **probabilistic data linkage** using Splink.

The goal is to simulate a real-world scenario where the same individuals appear in **two separate systems**, but without a reliable shared identifier, and then use probabilistic matching to link them.

---

## 🧠 Problem

In many real-world systems (e.g. healthcare, finance), records:

- do **not share a unique ID**
- contain **inconsistent or noisy data**
- may refer to the **same underlying person**

Example:

| System A        | System B        |
|----------------|----------------|
| Katherine Smith | Katie Smyth    |
| DOB matches     | DOB matches    |
| Postcode differs slightly | Postcode formatted differently |

A simple exact match would fail.

---

## 🎯 Goal

- Generate **synthetic datasets** with realistic errors
- Use **probabilistic linkage (Splink)** to identify matches
- Produce **match scores** between records

---

## 📁 Project Structure
splink-synthetic-linkage/
├─ data/
│  ├─ raw/
│  │  ├─ hospital_a.csv
│  │  ├─ hospital_b.csv
│  │  └─ ground_truth_links.csv
│  └─ output/
│     └─ predictions.csv
├─ src/
│  ├─ generate_synthetic_data.py
│  └─ run_linkage.py
├─ requirements.txt
└─ README.md


---

## ⚙️ Setup

Install dependencies:

```bash
pip install -r requirements.txt
```

## 🧪 Step 1 — Generate Synthetic Data
```bash
python src/generate_synthetic_data.py
```

## Step 2 - Run Linkage
```bash
python src/run_linkage.py
```

## 🧠 How Splink Works

Splink uses probabilistic modelling rather than exact matching.

It estimates:

- m probability → how often fields match for true matches
- u probability → how often fields match for non-matches

From this, it calculates:

- match weight
- match probability

---

## ⚙️ Blocking

Splink does not compare every record with every other record.

Instead, it uses blocking rules to limit comparisons.

Example:

block_on("surname")

---

## 📊 Current State

- Pipeline runs
- Predictions generated
- Model not fully trained yet

---

## 🚀 Next Steps

1. Sort predictions by match_probability
2. Estimate prior match probability
3. Train m parameters (EM)
4. Re-run predictions
5. Compare with ground truth

---

## 🧭 Continue Next Time

Start by adding training steps in run_linkage.py and re-running the model.
