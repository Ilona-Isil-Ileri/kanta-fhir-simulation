# Finnish Kanta-Oriented FHIR Data Simulation (Python) 🏥

A simple simulation script demonstrating how external health data (like blood glucose values) can be converted, clinically evaluated, and structured into Finland's national **Kanta / FHIR** format (including medication workflow).

---

## 📌 Project Overview
In Finland's healthcare ecosystem, raw laboratory data from external sources (e.g., blood glucose in `{mg/dL}`) needs to match national standards (like `{mmol/L}`, LOINC codes, and THL OIDs). 

Since this is a simple simulation for learning and exploring the ecosystem, I built a single-patient mock scenario to understand how the process works:
1. **Unit Conversion:** Converts raw blood glucose from mg/dL to mmol/L.
2. **Clinical Check:** Evaluates the converted value against reference ranges (e.g., flagging > 7.0 mmol/L as "High").
3. **FHIR Formatting & Medication:** Packages the mock patient, observation, and medication context into basic HL7 FHIR JSON structures.

*(Note: To keep the script simple and error-free, the mock patient data is defined directly inside the script rather than loaded from an external system.)*

---

## 🔄 Workflow Summary

```text
[Raw Input: Matti | 130 mg/dL]
         │
         ▼ (Clinical & Technical Logic)
 1. Unit Conversion: 130 / 18 = 7.22 mmol/L
 2. Clinical Check: 7.22 > 7.0 (Threshold) -> Status: HIGH ("H")
 3. Standard Mapping: FHIR Observation & MedicationRequest + LOINC, UCUM, THL OIDs
         │
         ▼
[Standardized FHIR Output]
 -> Subject: Patient/kanta-patient-001
 -> Observation: LOINC 15074-8 (7.22 mmol/L, Status: "H")
 -> MedicationRequest: Metformin (Clinical Follow-up)
```

---

## 🛠️ Concepts & Standards Covered

* **Interoperability Standards:** HL7 FHIR R4, LOINC, UCUM (units), ATC (medications), and THL OIDs (Finnish national identifiers).

* **Language & Libraries:** Python (fhir.resources).

* **Focus:** Understanding the data flow between external health data sources and national e-health systems.

---

## 🤖 AI Assistance Note

This small simulation script was built with the guidance of **Google Gemini**. While the AI helped generate the Python syntax and FHIR JSON templates, the core goal was for me to understand how Finnish health data standards and clinical logic connect in practice. The clinical logic, unit conversion rules, threshold evaluations, and overall workflow decisions were directed from my clinical domain background.

---

## 🚀 How to Run

1. Clone or download this repository:
   git clone [https://github.com/Ilona-Isil-Ileri/kanta-fhir-simulation.git](https://github.com/Ilona-Isil-Ileri/kanta-fhir-simulation.git)
2. Make sure you have the required library installed:
   pip install fhir.resources
3. Run the simulation script from your terminal:
   python project.py
   
