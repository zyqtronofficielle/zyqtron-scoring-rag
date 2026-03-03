import sys, json, os
from datetime import datetime

RANKINGS_FILE = "E:/QuantumForge/ai_rankings.json"
TEMP_DIR      = "E:/QuantumForge/temp"

LEVELS = [
    (85, 80, "Docteur Honoris Causa"),
    (75, 70, "Docteur"),
    (65, 60, "Post-Doctorant"),
    (55, 50, "Doctorant"),
    (0,  0,  "Master"),
]

def load():
    if os.path.exists(RANKINGS_FILE):
        with open(RANKINGS_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {}

def save(data):
    with open(RANKINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def doctorate_level(avg, rate, runs):
    if runs < 3: return "Candidat"
    for min_avg, min_rate, label in LEVELS:
        if avg >= min_avg and rate >= min_rate:
            return label
    return "Master"

def rerank(data):
    ranked = sorted(data.items(), key=lambda x: x[1].get("avg_score", 0), reverse=True)
    for rank, (model, _) in enumerate(ranked, 1):
        data[model]["rank"] = rank

def record(model, framework, score, attempts, success):
    attempts = attempts if attempts is not None else 3
    score    = score    if score    is not None else 0
    data = load()
    if model not in data:
        data[model] = {"total_runs": 0, "successes": 0, "total_score": 0,
                       "total_attempts": 0, "best_score": 0, "worst_score": 100,
                       "frameworks": {}, "history": [], "rank": None, "doctorate_level": "Candidat"}
    m = data[model]
    m["total_runs"]     += 1
    m["total_attempts"] += attempts
    if success:
        m["successes"]   += 1
        m["total_score"] += score
        m["best_score"]   = max(m["best_score"], score)
        m["worst_score"]  = min(m["worst_score"], score)
    fw = m["frameworks"].setdefault(framework, {"runs": 0, "total_score": 0})
    fw["runs"]        += 1
    fw["total_score"] += score if success else 0
    m["history"].append({"date": datetime.now().isoformat()[:16], "framework": framework,
                         "score": score, "attempts": attempts, "success": success})
    m["history"] = m["history"][-50:]
    avg  = m["total_score"] / m["successes"] if m["successes"] > 0 else 0
    rate = m["successes"] / m["total_runs"] * 100
    m["avg_score"]        = round(avg, 1)
    m["success_rate_pct"] = round(rate, 1)
    m["avg_attempts"]     = round(m["total_attempts"] / m["total_runs"], 2)
    m["doctorate_level"]  = doctorate_level(avg, rate, m["total_runs"])
    rerank(data)
    save(data)
    print(f"[Doctorat] {model} | Score: {score} | Moy: {avg:.1f} | Niveau: {m['doctorate_level']}")

def leaderboard():
    data = load()
    if not data:
        print("Aucun modele enregistre.")
        return
    ranked = sorted(data.items(), key=lambda x: x[1].get("avg_score", 0), reverse=True)
    print("\n  PROGRAMME DOCTORAT IA - LEADERBOARD")
    print(f"  {'#':<3} {'Modele':<38} {'Moy':>5} {'Reuss%':>7} {'Runs':>5} Niveau")
    for i, (model, s) in enumerate(ranked, 1):
        print(f"  {i:<3} {model[:38]:<38} {s.get('avg_score',0):>5.1f} {s.get('success_rate_pct',0):>6.1f}% {s.get('total_runs',0):>5} {s.get('doctorate_level','')}")

if __name__ == "__main__":
    os.makedirs(TEMP_DIR, exist_ok=True)
    cmd = sys.argv[1] if len(sys.argv) > 1 else "leaderboard"
    if cmd == "record":
        with open(f"{TEMP_DIR}/input_rankings.json", encoding="utf-8-sig") as f:
            d = json.load(f)
        record(d["model"], d["framework"], d["score"], d["attempts"], d["success"])
    elif cmd == "leaderboard":
        leaderboard()
