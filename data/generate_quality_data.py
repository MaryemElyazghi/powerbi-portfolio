import pandas as pd
import numpy as np
from faker import Faker
from datetime import datetime, timedelta
import random

# Initialize Faker with French locale for Moroccan names/context
fake = Faker('fr_FR')
np.random.seed(42)

# Configuration
n_records = 2000
categories = ["Retour produit", "Défaut qualité", "Délai livraison", "Erreur commande", "Endommagement"]
statuts = ["Résolu", "En cours", "Escaladé", "Fermé"]
regions = ["Casablanca", "Rabat", "Tanger", "Marrakech", "Agadir"]
produits = ["Technologie", "Mobilier", "Fournitures bureau"]
start_date = datetime(2023, 1, 1)

data = []

for i in range(n_records):
    # Date logic
    date_incident = start_date + timedelta(days=random.randint(0, 730))
    
    # Logic: Only resolved/closed incidents should have a resolution time
    statut = random.choice(statuts)
    delai_res = random.randint(1, 45) if statut in ["Résolu", "Fermé"] else np.nan
    
    # Logic: Satisfaction score often correlates with severity
    severite = random.choice(["Faible", "Moyen", "Élevé", "Critique"])
    base_score = random.uniform(2.5, 5.0) if severite == "Faible" else random.uniform(1.0, 3.5)
    
    data.append({
        "ID_Incident": f"INC-{i+1:05d}",
        "Date_Incident": date_incident.strftime("%Y-%m-%d"),
        "Categorie": random.choice(categories),
        "Produit": random.choice(produits),
        "Region": random.choice(regions),
        "Statut": statut,
        "Severite": severite,
        "Delai_Resolution_Jours": delai_res,
        "Satisfaction_Score": round(base_score, 1),
        "Cout_Incident": round(random.uniform(50, 5000), 2),
        "Technicien": fake.name(),
        "Resolu": 1 if statut in ["Résolu", "Fermé"] else 0
    })

# DataFrame creation
df = pd.DataFrame(data)

# Export
df.to_csv("incidents_qualite.csv", index=False, encoding="utf-8-sig")

print(f"✅ Dataset generated: {len(df)} quality incidents saved to 'incidents_qualite.csv'")
print("\n--- Summary Statistics ---")
print(df.describe())