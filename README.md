# PII Detector and Redactor

## Purpose

This project is a solution for the "Real-time PII Defense" challenge in Project Guardian 2.0. It processes a CSV file with JSON-formatted data records, detects standalone and combinatorial Personally Identifiable Information (PII) based on strict definitions, redacts/masks the identified PII, and outputs a new CSV file with the redacted data and a boolean flag (`is_pii`) indicating if PII was present in each record. The goal is to prevent data leaks in logs, APIs, and internal tools by sanitizing sensitive information in real-time.

## Overview

The script uses a rule-based approach with regular expressions for detecting well-structured PII (e.g., phone numbers, Aadhar) and logical checks for combinatorial PII (e.g., full name combined with email or address). Standalone PII is always redacted if detected. Combinatorial PII is only flagged and redacted when specific combinations appear in the same record to avoid false positives. Masking functions preserve partial data for debugging while obscuring sensitive parts (e.g., `98XXXXXX10` for phones).

This implementation prioritizes accuracy (target F1-score ≥0.95), efficiency (O(1) per record), and minimal false positives, as per the task's scoring system.

## Dependencies

- Python 3.8 or higher
- No external libraries required; uses only standard Python modules (`json`, `csv`, `re`, `sys`, `ast`).

## Setup

1. Clone the repository.
2. Ensure Python 3.8+ is installed on your system.

No virtual environment or installations needed.

## How to Run

Run the script with the input CSV file as an argument:

```bash
python3 detector_prabudh_kumar_yadav.py iscp_pii_dataset.csv
```
