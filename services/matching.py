from models.item import Item

def normalize(value):
    return (value or "").strip().lower()

def score_items(lost, found):
    if lost.category.lower() != found.category.lower():
        return 0.0

    score = 35
    fields = [("brand", 15), ("model", 15), ("color", 10), ("location", 15)]
    for field, points in fields:
        a, b = normalize(getattr(lost, field)), normalize(getattr(found, field))
        if a and b and a == b:
            score += points

    if lost.date == found.date:
        score += 5

    ld = set(normalize(lost.details).split())
    fd = set(normalize(found.details).split())
    if ld and fd:
        overlap = len(ld & fd) / max(1, len(ld | fd))
        score += round(overlap * 5, 2)

    return min(score, 100.0)

def generate_possible_matches(found):
    candidates = Item.query.filter_by(type="lost", status="searching").all()
    results = []
    for lost in candidates:
        s = score_items(lost, found)
        if s >= 55:
            results.append((lost, s))
    return sorted(results, key=lambda x: x[1], reverse=True)
