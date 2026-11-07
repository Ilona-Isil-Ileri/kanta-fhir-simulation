import json
from fhir.resources.patient import Patient
from fhir.resources.humanname import HumanName
from fhir.resources.identifier import Identifier

from fhir.resources.observation import Observation
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.coding import Coding
from fhir.resources.quantity import Quantity
from fhir.resources.reference import Reference

from fhir.resources.medicationrequest import MedicationRequest
from fhir.resources.dosage import Dosage
from fhir.resources.codeablereference import CodeableReference

# ==============================================================================
# STEP 1: PATIENT RESOURCE CREATION (Potilastiedot)
# ==============================================================================

# Create a FHIR Patient resource representing a Finnish patient (Potilas)
patient = Patient()

# System internal resource identifier
patient.id = "kanta-patient-001"

# Finnish National Personal Identity Code (Henkilötunnus / HETU)
# Official Finnish Social and Health Data Institute (THL) OID prefix: 1.2.246.21
hetu_identifier = Identifier()
hetu_identifier.system = "urn:oid:1.2.246.21"  # THL / Kanta national OID namespace
hetu_identifier.value = "010190-123A"          # Example HETU (Henkilötunnus)
patient.identifier = [hetu_identifier]

# Official Name (Nimi: Sukunimi ja Etunimi)
name = HumanName()
name.family = "Meikäläinen"    # Surname (Sukunimi)
name.given = ["Matti"]         # Given name (Etunimi)
name.use = "official"
patient.name = [name]

# Gender & Birth Date (Sukupuoli ja Syntymäaika)
patient.gender = "male"
patient.birthDate = "1990-01-01"

# Record Status (Aktiivinen potilastieto)
patient.active = True

# Convert Python FHIR object to Kanta-compliant JSON format
patient_json = patient.json(indent=2)

print("=== FINNISH KANTA-COMPLIANT FHIR PATIENT RESOURCE ===")
print(patient_json)


# ==============================================================================
# STEP 2: CLINICAL DECISION & UNIT CONVERSION LOGIC
# ==============================================================================

# 1. Incoming raw device/lab data (e.g., from an external medical device in mg/dL)
raw_glucose_value = 130.0  # mg/dL
raw_unit = "mg/dL"

# 2. Unit Mapping & Conversion (Birim Muunnos: mg/dL -> mmol/L)
# Converts US/legacy mg/dL to Finnish Kanta standard (mmol/L), dividing by 18.0
if raw_unit == "mg/dL":
    glucose_mmol = round(raw_glucose_value / 18.0, 1)  # Evaluates to 7.2 mmol/L
else:
    glucose_mmol = raw_glucose_value

# 3. Clinical Decision Support Logic (Kliininen päätöksentuki)
# Evaluates glycemic thresholds for fasting glucose
if glucose_mmol > 7.0:
    interp_code = "H"       # High / Koholla (Hyperglycemia threshold)
    interp_display = "High"
    clinical_note_text = "Fasting glucose elevated above diagnostic threshold (>7.0 mmol/L)."
elif glucose_mmol < 3.9:
    interp_code = "L"       # Low / Alhainen (Hypoglycemia risk)
    interp_display = "Low"
    clinical_note_text = "Fasting glucose below normal range (<3.9 mmol/L)."
else:
    interp_code = "N"       # Normal / Normaali
    interp_display = "Normal"
    clinical_note_text = "Fasting glucose within normal physiological reference range."


# ==============================================================================
# STEP 3: LABORATORY OBSERVATION RESOURCE CREATION (Laboratorio-tulos)
# ==============================================================================

# 1. Define mandatory codes FIRST
category_coding = Coding(
    system="http://terminology.hl7.org/CodeSystem/observation-category",
    code="laboratory",
    display="Laboratory"
)
category_concept = CodeableConcept(coding=[category_coding])

lab_code = Coding(
    system="http://loinc.org",
    code="15074-8",
    display="Glucose [Moles/volume] in Blood by Glucose oxidase method"
)
lab_concept = CodeableConcept(
    coding=[lab_code],
    text="fP-Gluk (Paastoverensokeri)"  # Finnish lab terminology
)

# 2. Instantiate Observation WITH REQUIRED FIELDS (status and code are MANDATORY in FHIR)
observation = Observation(
    status="final",  # Final validated result (Valmis laboratorio-tulos)
    code=lab_concept, # MANDATORY LOINC/THL Code
    category=[category_concept]
)

# Internal Resource Identifier
observation.id = "kanta-obs-001"

# Link Observation to Patient (Potilasviite -> Matti Meikäläinen)
patient_ref = Reference(
    reference="Patient/kanta-patient-001",
    display="Matti Meikäläinen"
)
observation.subject = patient_ref

# Timestamp of specimen collection (Näytteenottoaika)
observation.effectiveDateTime = "2026-10-16T08:00:00+02:00"

# Set Converted Value & Standard Unit (Tuloksen arvo ja yksikkö: 7.2 mmol/L)
value_quantity = Quantity(
    value=glucose_mmol,
    unit="mmol/l",
    system="http://unitsofmeasure.org",
    code="mmol/L"
)
observation.valueQuantity = value_quantity

# Set Clinical Interpretation (Tulkinta: High / Koholla)
interpretation_coding = Coding(
    system="http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation",
    code=interp_code,
    display=interp_display
)
interpretation_concept = CodeableConcept(coding=[interpretation_coding])
observation.interpretation = [interpretation_concept]

# Convert Python Observation object to Kanta-compliant JSON format
observation_json = observation.json(indent=2)

print("=== FINNISH KANTA-COMPLIANT FHIR OBSERVATION RESOURCE ===")
print(observation_json)



# ==============================================================================
# STEP 4: MEDICATION REQUEST RESOURCE CREATION (Lääkemääräys / Metformin)
# ==============================================================================

# 1. Define mandatory codes & references FIRST
med_code = Coding(
    system="http://www.whocc.no/atc",
    code="A10BA02",
    display="Metformin"
)
med_concept = CodeableConcept(
    coding=[med_code],
    text="Metformin 500 mg tablet"  # Local trade/dispense description
)

# FHIR R5 Standard: Wrap CodeableConcept inside CodeableReference
med_codeable_ref = CodeableReference(concept=med_concept)

patient_ref = Reference(
    reference="Patient/kanta-patient-001",
    display="Matti Meikäläinen"
)

# 2. Instantiate MedicationRequest WITH REQUIRED FIELDS
med_request = MedicationRequest(
    status="active",             # Active prescription (Voimassa oleva resepti)
    intent="order",              # Formal clinical order
    medication=med_codeable_ref, # Drug definition wrapped in CodeableReference
    subject=patient_ref          # Mandatory patient reference
)

# Internal Resource Identifier
med_request.id = "kanta-medreq-001"

# 3. Link Clinical Reason (Kliininen peruste -> Paastoverensokeri 7.2 mmol/L)
# Directly references the high fasting glucose observation resource from Step 3
reason_ref = Reference(
    reference="Observation/kanta-obs-001",
    display="Elevated Fasting Glucose (7.2 mmol/L)"
)

# FHIR R5: reason field uses CodeableReference wrapper
reason_codeable_ref = CodeableReference(reference=reason_ref)
med_request.reason = [reason_codeable_ref]

# 4. Dosage & Administration Instructions (Annostusohje)
dosage = Dosage(
    text="1 tablet orally once daily with meal (1 tab/vrk aterian yhteydessä)"
)
med_request.dosageInstruction = [dosage]

# Timestamp of prescription creation (Määräyspäivämäärä)
med_request.authoredOn = "2026-10-17T10:00:00+02:00"

# Convert Python MedicationRequest object to Kanta-compliant JSON format
med_request_json = med_request.json(indent=2)

print("=== FINNISH KANTA-COMPLIANT FHIR MEDICATION REQUEST RESOURCE ===")
print(med_request_json)