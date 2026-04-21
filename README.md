# FORScan Log Analyzer

A simple web-based tool for visualizing and analyzing CSV logs (e.g. FORScan / ECU logs) using interactive graphs.

---

## 📌 Overview

This application allows you to:

* Upload CSV log files
* Select parameters (columns) to visualize
* Plot multiple graphs based on time
* Compare different sensor values
* Analyze engine behavior (boost, EGR, MAF, DPF, etc.)

Designed primarily for automotive diagnostics, especially Mazda Skyactiv-D engines, but works with any structured CSV logs.

---

## 🚀 Features

* Interactive charts in browser (Streamlit UI)
* Multiple graphs per session
* Flexible column selection
* Handles large datasets
* Supports comparison of different scale signals

---

## 🛠 Requirements

* Python 3.8+
* pip

---

## 📦 Installation

```bash
git clone https://github.com/your-username/forscan-log-analyzer.git
cd forscan-log-analyzer
pip install -r requirements.txt
```

---

## ▶️ Run the App

```bash
streamlit run app.py
```

Then open in browser:

```
http://localhost:8501
```

---

## 📊 Usage

1. Upload your CSV file
2. Select **time column** (e.g. `time(ms)`)
3. Choose parameters to plot
4. Create multiple graphs by repeating selection
5. Analyze trends (boost vs desired, MAF vs MAP, etc.)

---

## 📁 Example Data

Typical useful parameters:

* MAP / MAP_DSD
* BP_A_ACT / BP_A_CMD
* MAF
* EGRP / EGRP_ACT
* PM_ACC / PM_ACC_DSD
* DP_DPF

---

## ⚠️ Notes

* If values have different scales, use separate graphs
* Large logs may take time to render
* Column names must match CSV headers exactly

---

## 🌐 Deployment

### Streamlit Cloud (recommended)

1. Push project to GitHub
2. Go to https://share.streamlit.io
3. Select repository
4. Deploy

### Local Server

```bash
streamlit run app.py --server.address 0.0.0.0
```

---

## 🧠 Use Cases

* Diagnosing turbo / boost issues
* EGR behavior analysis
* DPF regeneration tracking
* Fuel vs air correlation
* Sensor validation
