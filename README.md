# Sync Smart AI - Driven GitHub Sync POC

## Problem

In ServiceNow CI/CD implementation, Update Sets are committed to GitHub without built-in validation or conflict detection. This can cause deployment failures, rework, debugging delays, and operational overhead.

## POC Objective

Build a pre-sync validation utility that checks ServiceNow Update Sets before GitHub sync.

## Day 1 Scope

- GitHub repo setup
- Sample Update Set XML files
- Basic XML parser
- Rule-based validation engine
- Confidence score
- HTML validation report

## Validation Rules

- Duplicate sys_id conflict
- Hardcoded password/token/API key
- current.update() usage
- Missing dependency
- Basic naming warning

## How to Run

```bash
python src/main.py