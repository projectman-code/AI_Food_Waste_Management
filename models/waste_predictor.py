"""
Transparent baseline waste estimator for a college prototype.
It uses a simple rule-based model so it works offline without downloading weights.
Replace/validate it with a model trained on real local inventory data before deployment.
"""
def predict_waste(stock_kg, expected_demand_kg, days_to_expiry, temperature_c):
    if min(stock_kg, expected_demand_kg) < 0 or days_to_expiry < 0:
        raise ValueError("Inputs cannot be negative")
    surplus = max(0.0, stock_kg - expected_demand_kg)
    risk = 0
    reasons = []
    if surplus > 0:
        risk += 35
        reasons.append("stock is higher than expected demand")
    if days_to_expiry <= 1:
        risk += 40
        reasons.append("expiry is within one day")
    elif days_to_expiry <= 3:
        risk += 20
        reasons.append("expiry is within three days")
    if temperature_c >= 30:
        risk += 15
        reasons.append("high ambient temperature may accelerate spoilage")
    elif temperature_c >= 25:
        risk += 8
        reasons.append("warm ambient temperature")
    risk = min(risk, 100)
    if risk >= 65:
        level = "High"
    elif risk >= 30:
        level = "Medium"
    else:
        level = "Low"
    estimated_waste = round(min(stock_kg, surplus * (0.75 if risk >= 65 else 0.45 if risk >= 30 else 0.15)), 2)
    actions = []
    if surplus > 0:
        actions.append(f"Prioritize selling or donating up to {round(surplus,2)} kg of surplus stock.")
    if days_to_expiry <= 3:
        actions.append("Use first-expiring-first-out (FEFO) and label the batch clearly.")
    if temperature_c >= 25:
        actions.append("Check cold-storage conditions and follow the food's safe storage guidance.")
    if not actions:
        actions.append("Stock appears aligned with demand; keep monitoring inventory.")
    return {
        "risk": risk, "level": level, "surplus_kg": round(surplus,2),
        "estimated_waste_kg": estimated_waste,
        "reasons": reasons or ["no major risk indicators found"],
        "actions": actions
    }
