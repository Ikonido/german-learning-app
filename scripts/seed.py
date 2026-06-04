"""
Seed initial German vocabulary data.
Run: python scripts/seed.py
"""
import sys
import os

# Allow running from project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy.orm import Session

from app.db.session import SessionLocal, engine
from app.models import Word, NounDetail, VerbDetail, WordType, Gender, Auxiliary


def seed():
    db: Session = SessionLocal()

    # Check if already seeded
    if db.query(Word).first():
        print("Database already has words. Skipping seed.")
        db.close()
        return

    nouns = [
        # (german, translation, gender, plural, level, category)
        ("Haus", "дом", Gender.DAS, "Häuser", "A1", "home"),
        ("Tisch", "стол", Gender.DER, "Tische", "A1", "furniture"),
        ("Stuhl", "стул", Gender.DER, "Stühle", "A1", "furniture"),
        ("Buch", "книга", Gender.DAS, "Bücher", "A1", "education"),
        ("Katze", "кошка", Gender.DIE, "Katzen", "A1", "animals"),
        ("Hund", "собака", Gender.DER, "Hunde", "A1", "animals"),
        ("Apfel", "яблоко", Gender.DER, "Äpfel", "A1", "food"),
        ("Brot", "хлеб", Gender.DAS, "Brote", "A1", "food"),
        ("Frau", "женщина", Gender.DIE, "Frauen", "A1", "people"),
        ("Mann", "мужчина", Gender.DER, "Männer", "A1", "people"),
        ("Kind", "ребёнок", Gender.DAS, "Kinder", "A1", "people"),
        ("Auto", "машина", Gender.DAS, "Autos", "A1", "transport"),
        ("Straße", "улица", Gender.DIE, "Straßen", "A1", "city"),
        ("Schule", "школа", Gender.DIE, "Schulen", "A1", "education"),
        ("Wasser", "вода", Gender.DAS, "Wasser", "A1", "food"),
    ]

    verbs = [
        # (german, translation, praeteritum, perfekt, auxiliary, level, category)
        ("gehen", "идти, ходить", "ging", "gegangen", Auxiliary.SEIN, "A1", "motion"),
        ("kommen", "приходить", "kam", "gekommen", Auxiliary.SEIN, "A1", "motion"),
        ("machen", "делать", "machte", "gemacht", Auxiliary.HABEN, "A1", "general"),
        ("haben", "иметь", "hatte", "gehabt", Auxiliary.HABEN, "A1", "auxiliary"),
        ("sein", "быть", "war", "gewesen", Auxiliary.SEIN, "A1", "auxiliary"),
        ("essen", "есть (принимать пищу)", "aß", "gegessen", Auxiliary.HABEN, "A1", "food"),
        ("trinken", "пить", "trank", "getrunken", Auxiliary.HABEN, "A1", "food"),
        ("sprechen", "говорить", "sprach", "gesprochen", Auxiliary.HABEN, "A1", "communication"),
        ("lesen", "читать", "las", "gelesen", Auxiliary.HABEN, "A1", "education"),
        ("schreiben", "писать", "schrieb", "geschrieben", Auxiliary.HABEN, "A1", "education"),
        ("lernen", "учить, учиться", "lernte", "gelernt", Auxiliary.HABEN, "A1", "education"),
        ("spielen", "играть", "spielte", "gespielt", Auxiliary.HABEN, "A1", "leisure"),
        ("fahren", "ехать (на транспорте)", "fuhr", "gefahren", Auxiliary.SEIN, "A1", "motion"),
        ("stehen", "стоять", "stand", "gestanden", Auxiliary.HABEN, "A1", "general"),
        ("sitzen", "сидеть", "saß", "gesessen", Auxiliary.HABEN, "A1", "general"),
    ]

    print("Seeding nouns...")
    for german, translation, gender, plural, level, category in nouns:
        word = Word(
            german=german,
            translation=translation,
            word_type=WordType.NOUN,
            level=level,
            category=category,
            example_sentence=None,
        )
        db.add(word)
        db.flush()  # get id

        detail = NounDetail(
            word_id=word.id,
            gender=gender,
            plural=plural,
        )
        db.add(detail)

    print("Seeding verbs...")
    for german, translation, praeteritum, perfekt, auxiliary, level, category in verbs:
        word = Word(
            german=german,
            translation=translation,
            word_type=WordType.VERB,
            level=level,
            category=category,
        )
        db.add(word)
        db.flush()

        detail = VerbDetail(
            word_id=word.id,
            praeteritum=praeteritum,
            perfekt=perfekt,
            auxiliary=auxiliary,
        )
        db.add(detail)

    db.commit()
    print(f"Seeded {len(nouns)} nouns and {len(verbs)} verbs successfully!")
    db.close()


if __name__ == "__main__":
    seed()
