def calculate_severity(symptoms: list[str]) -> float:
    severity_map = {
        "chest pain": 90,
        "breathing difficulty": 85,
        "high fever": 70,
        "vomiting": 50,
        "headache": 30,
        "cough": 20,
        "cold": 10
    }

    score = 0

    for symptom in symptoms:
        score += severity_map.get(symptom.lower(), 5)

    return min(score, 100)