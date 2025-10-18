# Contributing to OLED Sonde Info Display

Thank you for your interest in contributing to **OLED Sonde Info Display**!  
This document outlines guidelines for reporting issues, suggesting features, and submitting pull requests.

---

## 1. Reporting Issues

If you encounter a bug or have a feature request:
- Check existing [Issues](../../issues) before creating a new one.
- Provide as much detail as possible:
  - Steps to reproduce
  - Expected vs. actual behavior
  - Logs or screenshots (if applicable)
  - Raspberry Pi model and OLED type

---

## 2. Development Setup

Requirements:
- Docker & Docker Compose
- Python 3.11+
- Access to a Raspberry Pi with I²C enabled (for testing)

To test locally:
```bash
docker compose up -d --build
```