# NIST CSF 2.0 + SOC 2 + ISO 27001 — Overview

Quick-reference notes on three major security frameworks, written in plain language for interview prep.

---

## NIST Cybersecurity Framework (CSF) 2.0

**Source:** [NIST CSWP 29 — The NIST Cybersecurity Framework (CSF) 2.0](https://doi.org/10.6028/NIST.CSWP.29) (Feb 26, 2024)

> Note: CSF 2.0 has **6** functions (added "Govern"), not the older 5-function version (CSF 1.1).

### Summary
- NIST CSF is a framework with six functions — **Govern, Identify, Protect, Detect, Respond, and Recover** — that help an organization manage cybersecurity risk from start to finish.
- **Govern** sits at the center because it sets the strategy and priorities that guide the other five functions, while Identify through Recover cover knowing your assets, defending them, spotting attacks, responding, and restoring operations.
- It also uses **Profiles** to compare where an organization's security stands today versus where it wants to be, and **Tiers** to measure how mature and consistent its security practices are.

### Structure
```
Function → Category → Subcategory
(e.g. Identify → Asset Management → "maintain hardware inventory")
```

### The 6 Functions
| Function | What it covers |
|---|---|
| Govern (GV) | Strategy, policy, roles/responsibilities, supply chain risk |
| Identify (ID) | Asset management, risk assessment, improvement |
| Protect (PR) | Access control, training, data security, platform security |
| Detect (DE) | Continuous monitoring, adverse event analysis |
| Respond (RS) | Incident management, analysis, mitigation, communication |
| Recover (RC) | Recovery plan execution, recovery communication |

### Profiles & Tiers
- **Current Profile** = where you are today. **Target Profile** = where you want to be. The gap = your action plan.
- **Tiers** (maturity, not required level of security): Tier 1 Partial → Tier 2 Risk Informed → Tier 3 Repeatable → Tier 4 Adaptive.

---

## SOC 2 (System and Organization Controls 2)

**Source:** AICPA standard; overview via Vanta / Drata blogs

### Summary
- SOC 2 is an independent audit report, created by the **AICPA**, that proves a company handles customer data securely — especially common for SaaS and cloud companies.
- It's built on five **Trust Service Criteria (TSC)** — Security, Availability, Processing Integrity, Confidentiality, and Privacy — where **Security is mandatory** and the other four are added based on what the business actually does.
- A **Type I** report checks if controls are designed correctly at one point in time, while a **Type II** report checks if those controls actually worked consistently over a period of **3–12 months** — Type II is the stronger proof.

### The 5 Trust Service Criteria
| Criteria | Description | Required? |
|---|---|---|
| Security (Common Criteria) | Baseline protection from unauthorized access | Yes — always required |
| Availability | Systems/data accessible when needed | Optional |
| Processing Integrity | Data processed accurately, completely, on time | Optional |
| Confidentiality | Confidential info restricted appropriately | Optional |
| Privacy | Personal data used only as agreed with the individual | Optional |

### Type I vs Type II
- **Type I** = a photo — controls exist and are designed correctly, checked once.
- **Type II** = a video — controls are tested for effectiveness over 3–12 months of actual operation.

---

## ISO 27001 (ISO/IEC 27001:2022)

**Source:** ISO/IEC 27001:2022 standard; overview via Secureframe, Sprinto, ISMS.online

> Note: The 2022 version has **93 controls in 4 themes** (Organizational, People, Physical, Technological), replacing the old 2013 version's 114 controls in 14 domains. Organizations had until Oct 31, 2025 to migrate — certificates on the 2013 version are no longer valid.

### Summary
- ISO 27001 is an international standard that certifies an organization has an **ongoing, well-run process** for managing information security — not just a one-time checklist.
- This ongoing process is called an **ISMS (Information Security Management System)**, where the organization continuously assesses risks, chooses controls, and improves over time.
- **Annex A** provides 93 possible controls across four themes — Organizational, People, Physical, and Technological — and the organization documents which ones it uses in a **Statement of Applicability (SoA)**.

### Annex A — 4 Themes (93 controls total)
| Theme | Covers |
|---|---|
| Organizational | Policies, responsibilities, supplier relationships, governance |
| People | Background checks, training, awareness, HR processes |
| Physical | Secure areas, environmental protection, physical access |
| Technological | Encryption, backups, logging, access control, secure dev |

### Key terms
- **ISMS** — the ongoing management system (policies + processes + controls), not just the tools.
- **Statement of Applicability (SoA)** — mandatory document listing which Annex A controls are used and why (or why not).

---

## Quick Comparison

| | NIST CSF | SOC 2 | ISO 27001 |
|---|---|---|---|
| Type | Voluntary framework | Audit report | Certifiable standard |
| Issued by | NIST (US govt) | AICPA (via CPA auditor) | ISO (international) |
| Focus | Risk management guidance | Trust/assurance for customers | Certified ISMS |
| Output | Organizational Profile | Audit report (Type I/II) | Certificate + SoA |

---
*Prepared as part of cloud security interview prep :- July 2026*
