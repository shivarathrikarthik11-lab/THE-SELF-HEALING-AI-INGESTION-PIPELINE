# Self-Healing Ingestion Pipeline

## Overview
This project implements a self-healing data ingestion pipeline using FastAPI.

## Features
- Data validation using Pydantic
- Anomaly detection using Z-score
- Self-healing (imputation)
- Confidence scoring

## How to Run

1. Install dependencies:
pip install -r requirements.txt

2. Run server:
uvicorn app:app --reload

3. Open:
http://127.0.0.1:8000/docs
