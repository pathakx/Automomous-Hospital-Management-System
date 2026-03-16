"""
symptom_tools.py  —  Week 5 Tool Layer

Provides AI-callable tools for symptom analysis:
  - recommend_department
  - analyze_symptoms

These tools are RULE-BASED and do NOT require a database session.
They use a static keyword-to-department mapping and symptom severity heuristics.

IMPORTANT: Always include the medical disclaimer in outputs.
These tools provide guidance only — they are NOT a medical diagnosis.
"""
import logging
from app.schemas.tool_result import ToolResult

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Static Symptom → Department Keyword Map
# Keys are lowercase keywords. Values are department names.
# Order matters: more specific keywords should appear before broad ones.
# ---------------------------------------------------------------------------
SYMPTOM_DEPARTMENT_MAP = {
    # Cardiology
    "chest pain": "Cardiology",
    "heart pain": "Cardiology",
    "palpitations": "Cardiology",
    "irregular heartbeat": "Cardiology",
    "heart": "Cardiology",

    # Dermatology
    "skin rash": "Dermatology",
    "rash": "Dermatology",
    "itching": "Dermatology",
    "acne": "Dermatology",
    "eczema": "Dermatology",
    "psoriasis": "Dermatology",
    "hair loss": "Dermatology",
    "skin": "Dermatology",

    # Orthopedics
    "joint pain": "Orthopedics",
    "bone pain": "Orthopedics",
    "back pain": "Orthopedics",
    "knee pain": "Orthopedics",
    "fracture": "Orthopedics",
    "muscle pain": "Orthopedics",
    "sprain": "Orthopedics",

    # Ophthalmology
    "eye pain": "Ophthalmology",
    "blurred vision": "Ophthalmology",
    "vision loss": "Ophthalmology",
    "eye": "Ophthalmology",
    "redness in eye": "Ophthalmology",

    # Gastroenterology
    "stomach pain": "Gastroenterology",
    "abdominal pain": "Gastroenterology",
    "nausea": "Gastroenterology",
    "vomiting": "Gastroenterology",
    "diarrhea": "Gastroenterology",
    "constipation": "Gastroenterology",
    "bloating": "Gastroenterology",
    "stomach": "Gastroenterology",

    # Neurology
    "headache": "Neurology",
    "migraine": "Neurology",
    "seizure": "Neurology",
    "dizziness": "Neurology",
    "numbness": "Neurology",
    "tingling": "Neurology",
    "memory loss": "Neurology",

    # Endocrinology
    "diabetes": "Endocrinology",
    "thyroid": "Endocrinology",
    "weight gain": "Endocrinology",
    "excessive thirst": "Endocrinology",
    "fatigue": "Endocrinology",

    # ENT (Ear, Nose, Throat)
    "sore throat": "ENT",
    "ear pain": "ENT",
    "hearing loss": "ENT",
    "nasal congestion": "ENT",
    "runny nose": "ENT",
    "sinusitis": "ENT",
    "tonsil": "ENT",

    # Pulmonology
    "cough": "Pulmonology",
    "shortness of breath": "Pulmonology",
    "wheezing": "Pulmonology",
    "asthma": "Pulmonology",
    "chest tightness": "Pulmonology",
    "breathing": "Pulmonology",

    # Urology
    "urinary pain": "Urology",
    "frequent urination": "Urology",
    "kidney pain": "Urology",
    "urination": "Urology",

    # Psychiatry
    "anxiety": "Psychiatry",
    "depression": "Psychiatry",
    "insomnia": "Psychiatry",
    "panic attack": "Psychiatry",
    "mood swings": "Psychiatry",

    # General Medicine (broad terms — match last)
    "fever": "General Medicine",
    "cold": "General Medicine",
    "flu": "General Medicine",
    "weakness": "General Medicine",
    "swelling": "General Medicine",
}

# ---------------------------------------------------------------------------
# Severity Heuristics
# Based on symptom count as a simple heuristic.
# ---------------------------------------------------------------------------
SEVERITY_LEVELS = {
    1: "mild",
    2: "mild",
    3: "moderate",
    4: "moderate",
}

MEDICAL_DISCLAIMER = (
    "⚠️ **Medical Disclaimer**: This assessment is for informational purposes only "
    "and does not constitute professional medical advice, diagnosis, or treatment. "
    "Please consult a qualified healthcare professional for proper evaluation."
)


# ---------------------------------------------------------------------------
# Tool 1: recommend_department
# ---------------------------------------------------------------------------
def recommend_department(symptoms: list[str]) -> ToolResult:
    """
    Maps a list of symptom strings to the most relevant hospital department.
    Uses keyword matching against SYMPTOM_DEPARTMENT_MAP (case-insensitive).

    Args:
        symptoms: A list of symptom strings e.g., ["chest pain", "dizziness"]

    Returns:
        ToolResult with data={"department": "Cardiology", "matched_on": "chest pain"},
        or error="no_matching_department" with a fallback to General Medicine.
    """
    logger.info(f"[Tool] recommend_department | symptoms={symptoms}")

    if not symptoms:
        return ToolResult(success=False, error="no_symptoms_provided")

    # Flatten all symptoms into a single lowercase string for partial matching
    symptoms_text = " ".join(s.lower() for s in symptoms)

    matched_department = None
    matched_keyword = None

    # Iterate in insertion order — more specific keywords appear first
    for keyword, department in SYMPTOM_DEPARTMENT_MAP.items():
        if keyword in symptoms_text:
            matched_department = department
            matched_keyword = keyword
            break

    if not matched_department:
        logger.info(
            f"[Tool] No keyword match found. Defaulting to General Medicine. "
            f"symptoms={symptoms}"
        )
        return ToolResult(
            success=False,
            error="no_matching_department",
            data={
                "department": "General Medicine",
                "matched_on": None,
                "note": "No specific department matched. Recommending General Medicine.",
            },
        )

    logger.info(
        f"[Tool] Department match: '{matched_keyword}' → {matched_department}"
    )
    return ToolResult(
        success=True,
        data={
            "department": matched_department,
            "matched_on": matched_keyword,
        },
    )


# ---------------------------------------------------------------------------
# Tool 2: analyze_symptoms
# ---------------------------------------------------------------------------
def analyze_symptoms(
    symptoms: list[str],
    age: int = None,
    duration: str = None,
) -> ToolResult:
    """
    Produces a full symptom assessment including severity, possible conditions,
    recommended hospital department, and a mandatory medical disclaimer.

    Args:
        symptoms: A list of symptom strings e.g., ["chest pain", "dizziness", "nausea"]
        age:      Optional patient age (int) for context.
        duration: Optional symptom duration string e.g., "3 days", "1 week".

    Returns:
        ToolResult with data={"severity": ..., "possible_conditions": [...],
        "recommended_department": ..., "disclaimer": ...}.
    """
    logger.info(
        f"[Tool] analyze_symptoms | symptoms={symptoms} | age={age} | duration={duration}"
    )

    if not symptoms:
        return ToolResult(success=False, error="no_symptoms_provided")

    # Step 1: Find recommended department
    dept_result = recommend_department(symptoms)
    recommended_department = (
        dept_result.data.get("department", "General Medicine")
        if dept_result.data
        else "General Medicine"
    )

    # Step 2: Determine severity based on symptom count
    symptom_count = len(symptoms)
    if symptom_count >= 5:
        severity = "severe"
    else:
        severity = SEVERITY_LEVELS.get(symptom_count, "moderate")

    # Escalate severity for alarm symptoms regardless of count
    alarm_keywords = ["chest pain", "shortness of breath", "vision loss", "seizure", "unconscious"]
    symptoms_lower = [s.lower() for s in symptoms]
    if any(alarm in " ".join(symptoms_lower) for alarm in alarm_keywords):
        severity = "severe"

    # Step 3: Build possible conditions list (keyword-based heuristic)
    possible_conditions = []
    symptoms_text = " ".join(symptoms_lower)
    condition_map = {
        "chest pain": "Possible cardiac event — seek immediate attention",
        "headache": "Tension headache, migraine, or hypertension",
        "fever": "Viral or bacterial infection",
        "nausea": "Gastroenteritis or food poisoning",
        "dizziness": "Inner ear problem, low blood pressure, or neurological cause",
        "cough": "Upper respiratory infection, bronchitis, or asthma",
        "rash": "Allergic reaction, dermatitis, or viral infection",
        "joint pain": "Arthritis, gout, or musculoskeletal strain",
        "fatigue": "Anemia, thyroid disorder, or viral illness",
        "shortness of breath": "Asthma, COPD, cardiac issue — seek immediate attention",
    }
    for kw, condition in condition_map.items():
        if kw in symptoms_text:
            possible_conditions.append(condition)

    if not possible_conditions:
        possible_conditions = ["Further clinical evaluation required"]

    # Step 4: Build the final result
    result_data = {
        "severity": severity,
        "symptoms_reported": symptoms,
        "possible_conditions": possible_conditions,
        "recommended_department": recommended_department,
        "disclaimer": MEDICAL_DISCLAIMER,
    }
    if age:
        result_data["age_provided"] = age
    if duration:
        result_data["duration_provided"] = duration

    logger.info(
        f"[Tool] analyze_symptoms result | severity={severity} | "
        f"department={recommended_department} | conditions={possible_conditions}"
    )
    return ToolResult(success=True, data=result_data)
