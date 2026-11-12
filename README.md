# Lab #10 — Python CI Pipeline & Secret Management

A small Flask UI + JSON API, built and tested using GitHub Actions. Security: **Semgrep** and **CodeQL** (SAST), **Trivy** (SCA + secret scan), **SOPS + age** (encrypted file with separate key), and **HashiCorp Vault KV v2** (read-only token).

**Start here:** [Полная инструкция на русском](README_RU.md).  
**Defense/report guide:** [English outline](REPORT_GUIDE_EN.md).

> This project is for local education. No real credentials, production Vault configurations, or private keys are provided. The actual CI results must be verified from your own GitHub Actions run.
