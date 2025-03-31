# ENEM Analysis Dashboard 📊

A comprehensive data analysis and visualization dashboard for the Brazilian National High School Exam (ENEM) results. This project provides interactive insights into student performance across different demographic groups, socioeconomic factors, and knowledge areas.

## Overview

The ENEM Analysis Dashboard is built using Streamlit and provides an intuitive interface to explore and analyze ENEM exam results. It features:

- Interactive filtering by various demographic and socioeconomic factors
- Detailed performance metrics across different knowledge areas
- Visual representations of score distributions
- Comparative analysis tools

## Features

- 📈 Real-time data filtering and visualization
- 🎯 Performance metrics for different knowledge areas:
  - Natural Sciences
  - Human Sciences
  - Language
  - Mathematics
- 🔍 Filter options:
  - Knowledge Area
  - Gender
  - Family Income
  - Internet Access
  - Number of Computers
- 📊 Multiple visualization types:
  - Bar charts
  - Histograms
  - Box plots

## Requirements

- Python 3.8+
- Dependencies listed in `requirements.txt`

## Installation

1. Clone the repository:
```bash
git clone https://github.com/joaomarcosmb/enem-analysis.git
cd enem-analysis
```

2. Create and activate a virtual environment (optional, but recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. Install the required packages:
```bash
pip install -r requirements.txt
```

## Usage

1. Ensure you have the required data file in the correct location:
```
src/data/processed/preprocessed_data.csv
```

2. Run the Streamlit application:
```bash
streamlit run app.py
```

3. Open your web browser and navigate to the http://localhost:8501 (if not opened automatically).

## Data Structure

The dashboard expects a preprocessed CSV file with the following columns:
- ID: Unique identifier for each student
- Natural Sciences: Score in Natural Sciences
- Human Sciences: Score in Human Sciences
- Language: Score in Language
- Mathematics: Score in Mathematics
- Sex: Student's gender
- Family Income: Family income in Brazilian Reais (R$)
- Internet Access: Binary indicator (Yes/No)
- Number of Computers: Count of computers at home

## Acknowledgments

- Data source: INEP (Instituto Nacional de Estudos e Pesquisas Educacionais Anísio Teixeira)
- Built with Streamlit, Pandas, and Plotly
