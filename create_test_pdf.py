from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import cm
import os

os.makedirs("data", exist_ok=True)

doc = SimpleDocTemplate(
    "data/test.pdf",
    pagesize=A4,
    rightMargin=2*cm, leftMargin=2*cm,
    topMargin=2*cm, bottomMargin=2*cm
)

styles = getSampleStyleSheet()
title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=16, spaceAfter=12)
h2_style = ParagraphStyle('H2', parent=styles['Heading2'], fontSize=13, spaceAfter=8)
body_style = ParagraphStyle('Body', parent=styles['Normal'], fontSize=11, spaceAfter=6, leading=16)

content = []

content.append(Paragraph("Guide Administratif Étudiant - ENISO", title_style))
content.append(Paragraph("Année Universitaire 2024-2025", body_style))
content.append(Spacer(1, 0.5*cm))

sections = [
    ("1. Procédures d'Inscription", [
        "L'inscription universitaire est obligatoire pour tous les nouveaux étudiants. Elle se déroule au Service de la Scolarité du 1er au 30 septembre.",
        "Documents requis : baccalauréat original, carte d'identité nationale, 4 photos d'identité, certificat médical, relevé de notes du baccalauréat.",
        "Les frais d'inscription sont de 150 dinars pour la licence et 200 dinars pour le master. Paiement par virement bancaire uniquement.",
        "En cas de dossier incomplet, l'étudiant dispose de 10 jours ouvrables pour compléter son dossier.",
    ]),
    ("2. Réinscription", [
        "La réinscription est obligatoire chaque année entre le 15 et le 31 juillet.",
        "Documents requis : carte étudiante de l'année précédente, relevé de notes certifié, attestation de paiement, deux photos d'identité.",
        "Les étudiants ayant des dettes ne peuvent pas se réinscrire avant régularisation.",
        "Une dérogation pour réinscription tardive peut être demandée auprès du Doyen avant le 15 août.",
    ]),
    ("3. Stages et PFE", [
        "Le stage est obligatoire : 2 mois minimum pour la licence, 4 mois minimum pour le master.",
        "Une convention de stage signée doit être soumise 15 jours avant le début du stage.",
        "Le sujet du PFE doit être soumis avant le 1er novembre pour une soutenance en juin.",
        "Le rapport de PFE doit être déposé en 3 exemplaires 15 jours avant la soutenance.",
        "En cas d'échec au PFE, l'étudiant peut demander un report dans un délai de 6 mois.",
    ]),
    ("4. Services Universitaires", [
        "Le Service de la Scolarité est ouvert du lundi au vendredi de 8h30 à 12h00 et de 13h30 à 16h30.",
        "La Bibliothèque est accessible de 8h00 à 20h00 en semaine. L'emprunt est limité à 5 livres pour 14 jours.",
        "Le Service Social propose des aides financières. Les demandes de bourses doivent être déposées avant le 30 octobre.",
        "Le Service Médical assure des consultations gratuites au bâtiment B de 9h00 à 16h00.",
    ]),
    ("5. Règlement et Discipline", [
        "L'assiduité est obligatoire. Plus de 20% d'absences entraîne l'interdiction de passer l'examen.",
        "La tricherie aux examens entraîne la note zéro et un avertissement officiel.",
        "Toute réclamation de notes doit être déposée dans les 5 jours suivant la publication des résultats.",
    ]),
]

for title, paragraphs in sections:
    content.append(Paragraph(title, h2_style))
    for para in paragraphs:
        content.append(Paragraph(para, body_style))
    content.append(Spacer(1, 0.3*cm))

doc.build(content)
print("✅ PDF créé : data/test.pdf")
