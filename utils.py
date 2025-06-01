import json

def load_professions():
    with open("professions.json", "r", encoding="utf-8") as file:
        return json.load(file)

def match_professions(selected_subjects):
    professions = load_professions()
    matched = []

    for prof in professions:
        if any(subject.lower() in selected_subjects for subject in prof.get("subjects", [])):
            matched.append(prof)

    return matched[:5]