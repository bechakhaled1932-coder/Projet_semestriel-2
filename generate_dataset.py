import json
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Questions ENISo dans plusieurs langues
questions = [
    # Français
    {"q": "Comment s'inscrire à l'ENISo ?", "lang": "fr"},
    {"q": "Quels documents pour le stage d'été ?", "lang": "fr"},
    {"q": "Quand a lieu la soutenance du PFE ?", "lang": "fr"},
    {"q": "Comment remplir le formulaire de stage ?", "lang": "fr"},
    {"q": "Quelle est la durée minimale du stage ?", "lang": "fr"},

    # Anglais
    {"q": "How to register at ENISo ?", "lang": "en"},
    {"q": "What documents are needed for the summer internship ?", "lang": "en"},
    {"q": "When is the PFE defense ?", "lang": "en"},
    {"q": "How to fill the internship form ?", "lang": "en"},
    {"q": "What is the minimum internship duration ?", "lang": "en"},

    # Arabe
    {"q": "كيف أتسجل في المدرسة الوطنية للمهندسين بسوسة؟", "lang": "ar"},
    {"q": "ما هي الوثائق المطلوبة لتسجيل التدريب الصيفي؟", "lang": "ar"},
    {"q": "متى يكون الدفاع عن مشروع نهاية الدراسة؟", "lang": "ar"},
    {"q": "كيف أملأ استمارة التدريب؟", "lang": "ar"},
    {"q": "ما هي المدة الدنيا للتدريب؟", "lang": "ar"},

    # Espagnol
    {"q": "¿Cómo inscribirse en ENISo?", "lang": "es"},
    {"q": "¿Qué documentos se necesitan para las prácticas?", "lang": "es"},
]

# Contexte ENISo
context = """
GUIDE ADMINISTRATIF ENISo

=== INSCRIPTION ET RÉINSCRIPTION ===
Pour s'inscrire à l'ENISo, l'étudiant doit fournir :
- Une copie de la carte d'identité nationale
- Les relevés de notes du baccalauréat
- Une photo d'identité récente
- Le reçu de paiement des frais d'inscription
La réinscription se fait chaque année au début de septembre.

=== STAGES ===
Le stage d'été est obligatoire pour tous les étudiants de 2ème année.
La durée minimale du stage est de 4 semaines.
L'étudiant doit déposer sa convention de stage au service des stages.
Le rapport de stage doit être remis avant le 30 septembre.

=== PFE ===
Le PFE est obligatoire en 3ème année d'ingénieur.
La soutenance du PFE a lieu en juin.
Le rapport final doit être déposé 2 semaines avant la soutenance.

=== CONTACTS ===
Scolarité : scolarite@eniso.u-sousse.tn
Stages : stages@eniso.u-sousse.tn
"""

dataset = []

for item in questions:
    print(f"Génération réponse pour : {item['q']}")
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": f"""Tu es un assistant administratif expert de l'ENISo.
Réponds UNIQUEMENT dans la langue de la question.
Utilise UNIQUEMENT les informations du contexte fourni.
Sois précis et concis."""
            },
            {
                "role": "user",
                "content": f"Contexte:\n{context}\n\nQuestion: {item['q']}"
            }
        ],
        temperature=0
    )
    
    answer = response.choices[0].message.content
    
    dataset.append({
        "instruction": item['q'],
        "input": context,
        "output": answer,
        "language": item['lang']
    })
    
    print(f"✅ Réponse générée en {item['lang']}")

# Sauvegarder le dataset
with open("dataset_eniso.json", "w", encoding="utf-8") as f:
    json.dump(dataset, f, ensure_ascii=False, indent=2)

print(f"\n🎉 Dataset créé : {len(dataset)} exemples")