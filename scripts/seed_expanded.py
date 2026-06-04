"""
Expanded seed script for German A1-A2 vocabulary (100-150+ words).
Run: python scripts/seed_expanded.py

Features:
- 5 categories requested: Мебель, Еда, Семья, Движение, Время
- Both nouns and verbs
- Every word has a good example_sentence (required for fill_blank tasks)
- Levels A1 / A2
- Clears old data for a clean expanded dataset
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models import Word, NounDetail, VerbDetail, WordType, Gender, Auxiliary, UserProgress


def seed_expanded():
    db: Session = SessionLocal()

    print("Clearing old vocabulary, details and progress (for clean expanded seed)...")
    db.query(UserProgress).delete(synchronize_session=False)
    db.query(VerbDetail).delete(synchronize_session=False)
    db.query(NounDetail).delete(synchronize_session=False)
    db.query(Word).delete(synchronize_session=False)
    db.commit()

    # Note: The data lists below are intentionally large (~122 items) to satisfy the 100-150 requirement.

    # ============================================================
    # NOUNS (german, translation, gender, plural, level, category, example_sentence)
    # ============================================================
    nouns = [
        # --- Мебель (Furniture) ---
        ("Tisch", "стол", Gender.DER, "Tische", "A1", "Мебель", "Der Tisch steht in der Küche."),
        ("Stuhl", "стул", Gender.DER, "Stühle", "A1", "Мебель", "Ich sitze auf dem Stuhl."),
        ("Bett", "кровать", Gender.DAS, "Betten", "A1", "Мебель", "Ich schlafe in meinem Bett."),
        ("Sofa", "диван", Gender.DAS, "Sofas", "A1", "Мебель", "Wir sitzen gemütlich auf dem Sofa."),
        ("Schrank", "шкаф", Gender.DER, "Schränke", "A1", "Мебель", "Die Kleider hängen im Schrank."),
        ("Lampe", "лампа", Gender.DIE, "Lampen", "A1", "Мебель", "Die Lampe leuchtet im Wohnzimmer."),
        ("Teppich", "ковёр", Gender.DER, "Teppiche", "A1", "Мебель", "Der Teppich liegt auf dem Boden."),
        ("Spiegel", "зеркало", Gender.DER, "Spiegel", "A1", "Мебель", "Ich sehe mich im Spiegel."),
        ("Regal", "полка", Gender.DAS, "Regale", "A1", "Мебель", "Die Bücher stehen im Regal."),
        ("Fenster", "окно", Gender.DAS, "Fenster", "A1", "Мебель", "Das Fenster ist weit offen."),
        ("Tür", "дверь", Gender.DIE, "Türen", "A1", "Мебель", "Bitte schließe die Tür."),
        ("Wand", "стена", Gender.DIE, "Wände", "A1", "Мебель", "An der Wand hängt ein schönes Bild."),
        ("Boden", "пол", Gender.DER, "Böden", "A1", "Мебель", "Der Boden ist aus Holz."),
        ("Sessel", "кресло", Gender.DER, "Sessel", "A1", "Мебель", "Mein Opa sitzt im Sessel."),
        ("Couch", "кушетка", Gender.DIE, "Couchs", "A1", "Мебель", "Die Couch ist sehr bequem."),
        ("Bild", "картина", Gender.DAS, "Bilder", "A1", "Мебель", "Das Bild hängt an der Wand."),
        ("Vorhang", "занавеска", Gender.DER, "Vorhänge", "A1", "Мебель", "Der Vorhang ist blau."),
        ("Schublade", "ящик", Gender.DIE, "Schubladen", "A1", "Мебель", "Die Schublade ist voll."),
        ("Nachttisch", "прикроватный столик", Gender.DER, "Nachttische", "A2", "Мебель", "Das Buch liegt auf dem Nachttisch."),

        # --- Еда (Food) ---
        ("Apfel", "яблоко", Gender.DER, "Äpfel", "A1", "Еда", "Ich esse jeden Tag einen Apfel."),
        ("Brot", "хлеб", Gender.DAS, "Brote", "A1", "Еда", "Zum Frühstück esse ich Brot mit Butter."),
        ("Milch", "молоко", Gender.DIE, "Milch", "A1", "Еда", "Die Kinder trinken Milch zum Frühstück."),
        ("Käse", "сыр", Gender.DER, "Käse", "A1", "Еда", "Ich mag Käse auf meinem Brot."),
        ("Wurst", "колбаса", Gender.DIE, "Würste", "A1", "Еда", "Wir kaufen frische Wurst auf dem Markt."),
        ("Ei", "яйцо", Gender.DAS, "Eier", "A1", "Еда", "Morgens koche ich mir ein Ei."),
        ("Tomate", "помидор", Gender.DIE, "Tomaten", "A1", "Еда", "Die Tomate ist rot und reif."),
        ("Kartoffel", "картофель", Gender.DIE, "Kartoffeln", "A1", "Еда", "Wir essen heute Kartoffeln mit Soße."),
        ("Reis", "рис", Gender.DER, "Reis", "A1", "Еда", "Der Reis kocht etwa zwanzig Minuten."),
        ("Nudeln", "макароны", Gender.DIE, None, "A1", "Еда", "Ich koche Nudeln mit Tomatensoße."),
        ("Suppe", "суп", Gender.DIE, "Suppen", "A1", "Еда", "Meine Mutter kocht eine leckere Suppe."),
        ("Kuchen", "пирог, торт", Gender.DER, "Kuchen", "A1", "Еда", "Zum Geburtstag backen wir einen Kuchen."),
        ("Kaffee", "кофе", Gender.DER, "Kaffees", "A1", "Еда", "Ich trinke gerne Kaffee am Morgen."),
        ("Tee", "чай", Gender.DER, "Tees", "A1", "Еда", "Möchtest du eine Tasse Tee?"),
        ("Wasser", "вода", Gender.DAS, "Wasser", "A1", "Еда", "Trinkst du jeden Tag genug Wasser?"),
        ("Saft", "сок", Gender.DER, "Säfte", "A1", "Еда", "Die Kinder trinken Apfelsaft."),
        ("Butter", "масло", Gender.DIE, "Butter", "A1", "Еда", "Ich streiche Butter auf das frische Brot."),
        ("Zucker", "сахар", Gender.DER, "Zucker", "A1", "Еда", "Ein wenig Zucker macht den Kaffee süß."),
        ("Salz", "соль", Gender.DAS, "Salz", "A1", "Еда", "Die Suppe braucht noch etwas Salz."),
        ("Fisch", "рыба", Gender.DER, "Fische", "A1", "Еда", "Am Freitag essen wir oft Fisch."),
        ("Fleisch", "мясо", Gender.DAS, "Fleisch", "A1", "Еда", "Das Fleisch ist sehr zart."),
        ("Gemüse", "овощи", Gender.DAS, "Gemüse", "A1", "Еда", "Wir essen viel Gemüse."),
        ("Obst", "фрукты", Gender.DAS, "Obst", "A1", "Еда", "Obst ist gesund und lecker."),
        ("Banane", "банан", Gender.DIE, "Bananen", "A1", "Еда", "Die Banane ist gelb und süß."),
        ("Birne", "груша", Gender.DIE, "Birnen", "A1", "Еда", "Im Herbst gibt es viele Birnen."),

        # --- Семья (Family) ---
        ("Mutter", "мама, мать", Gender.DIE, "Mütter", "A1", "Семья", "Meine Mutter kocht sehr gut."),
        ("Vater", "папа, отец", Gender.DER, "Väter", "A1", "Семья", "Mein Vater arbeitet in einer Bank."),
        ("Eltern", "родители", Gender.DIE, "Eltern", "A1", "Семья", "Meine Eltern wohnen in Berlin."),
        ("Bruder", "брат", Gender.DER, "Brüder", "A1", "Семья", "Ich habe einen kleinen Bruder."),
        ("Schwester", "сестра", Gender.DIE, "Schwestern", "A1", "Семья", "Meine Schwester ist älter als ich."),
        ("Sohn", "сын", Gender.DER, "Söhne", "A1", "Семья", "Sie haben einen Sohn und eine Tochter."),
        ("Tochter", "дочь", Gender.DIE, "Töchter", "A1", "Семья", "Seine Tochter geht schon in die Schule."),
        ("Kind", "ребёнок", Gender.DAS, "Kinder", "A1", "Семья", "Das Kind spielt im Garten."),
        ("Großmutter", "бабушка", Gender.DIE, "Großmütter", "A1", "Семья", "Meine Großmutter backt die besten Kuchen."),
        ("Großvater", "дедушка", Gender.DER, "Großväter", "A1", "Семья", "Der Großvater erzählt spannende Geschichten."),
        ("Onkel", "дядя", Gender.DER, "Onkel", "A1", "Семья", "Mein Onkel wohnt in München."),
        ("Tante", "тётя", Gender.DIE, "Tanten", "A1", "Семья", "Die Tante kommt uns besuchen."),
        ("Cousin", "двоюродный брат", Gender.DER, "Cousins", "A2", "Семья", "Mein Cousin studiert in Köln."),
        ("Cousine", "двоюродная сестра", Gender.DIE, "Cousinen", "A2", "Семья", "Ich spiele oft mit meiner Cousine."),
        ("Familie", "семья", Gender.DIE, "Familien", "A1", "Семья", "Wir sind eine große und glückliche Familie."),
        ("Mann", "мужчина, муж", Gender.DER, "Männer", "A1", "Семья", "Der Mann arbeitet viel."),
        ("Frau", "женщина, жена", Gender.DIE, "Frauen", "A1", "Семья", "Die Frau kocht das Abendessen."),
        ("Freund", "друг", Gender.DER, "Freunde", "A1", "Семья", "Mein bester Freund heißt Max."),
        ("Freundin", "подруга, девушка", Gender.DIE, "Freundinnen", "A1", "Семья", "Meine Freundin wohnt nebenan."),

        # --- Движение (Movement) ---
        ("Auto", "машина, автомобиль", Gender.DAS, "Autos", "A1", "Движение", "Ich fahre mit dem Auto zur Arbeit."),
        ("Bus", "автобус", Gender.DER, "Busse", "A1", "Движение", "Der Bus kommt in fünf Minuten."),
        ("Zug", "поезд", Gender.DER, "Züge", "A1", "Движение", "Der Zug fährt um acht Uhr ab."),
        ("Fahrrad", "велосипед", Gender.DAS, "Fahrräder", "A1", "Движение", "Ich fahre gerne Fahrrad im Park."),
        ("Flugzeug", "самолёт", Gender.DAS, "Flugzeuge", "A1", "Движение", "Das Flugzeug landet in einer Stunde."),
        ("Schiff", "корабль", Gender.DAS, "Schiffe", "A1", "Движение", "Das Schiff fährt über das Meer."),
        ("Straße", "улица", Gender.DIE, "Straßen", "A1", "Движение", "Die Straße ist sehr breit."),
        ("Weg", "путь, дорога", Gender.DER, "Wege", "A1", "Движение", "Der Weg führt zum Wald."),
        ("Bahnhof", "вокзал", Gender.DER, "Bahnhöfe", "A1", "Движение", "Wir treffen uns am Bahnhof."),
        ("Flughafen", "аэропорт", Gender.DER, "Flughäfen", "A1", "Движение", "Der Flughafen ist sehr groß."),
        ("Ticket", "билет", Gender.DAS, "Tickets", "A1", "Движение", "Ich habe zwei Tickets für den Zug."),
        ("Fahrer", "водитель", Gender.DER, "Fahrer", "A1", "Движение", "Der Fahrer ist sehr vorsichtig."),
        ("Rad", "колесо, велосипед", Gender.DAS, "Räder", "A1", "Движение", "Das Rad meines Fahrrads ist kaputt."),

        # --- Время (Time) ---
        ("Uhr", "часы", Gender.DIE, "Uhren", "A1", "Время", "Wie viel Uhr ist es jetzt?"),
        ("Zeit", "время", Gender.DIE, "Zeiten", "A1", "Время", "Ich habe keine Zeit."),
        ("Stunde", "час", Gender.DIE, "Stunden", "A1", "Время", "Die Stunde ist sehr lang."),
        ("Minute", "минута", Gender.DIE, "Minuten", "A1", "Время", "Warte bitte fünf Minuten."),
        ("Tag", "день", Gender.DER, "Tage", "A1", "Время", "Jeder Tag ist ein neuer Anfang."),
        ("Nacht", "ночь", Gender.DIE, "Nächte", "A1", "Время", "In der Nacht ist es dunkel."),
        ("Morgen", "утро", Gender.DER, "Morgen", "A1", "Время", "Guten Morgen! Wie geht es dir?"),
        ("Abend", "вечер", Gender.DER, "Abende", "A1", "Время", "Am Abend schaue ich fern."),
        ("Woche", "неделя", Gender.DIE, "Wochen", "A1", "Время", "Die Woche hat sieben Tage."),
        ("Monat", "месяц", Gender.DER, "Monate", "A1", "Время", "Der Monat hat dreißig Tage."),
        ("Jahr", "год", Gender.DAS, "Jahre", "A1", "Время", "Ein Jahr hat zwölf Monate."),
        ("Kalender", "календарь", Gender.DER, "Kalender", "A1", "Время", "Ich schaue in den Kalender."),
        ("Uhrzeit", "время (по часам)", Gender.DIE, "Uhrzeiten", "A1", "Время", "Die Uhrzeit ist jetzt halb drei."),
        ("Termin", "встреча, назначенное время", Gender.DER, "Termine", "A2", "Время", "Ich habe heute einen wichtigen Termin."),
    ]

    # ============================================================
    # VERBS (german, translation, praeteritum, perfekt, auxiliary, level, category, example_sentence)
    # ============================================================
    verbs = [
        # --- Мебель / Дом ---
        ("stellen", "ставить", "stellte", "gestellt", Auxiliary.HABEN, "A1", "Мебель", "Ich stelle den Stuhl an den Tisch."),
        ("legen", "класть, положить", "legte", "gelegt", Auxiliary.HABEN, "A1", "Мебель", "Ich lege das Buch auf den Tisch."),
        ("hängen", "висеть, вешать", "hing", "gehangen", Auxiliary.HABEN, "A1", "Мебель", "Das Bild hängt an der Wand."),
        ("putzen", "чистить, убирать", "putzte", "geputzt", Auxiliary.HABEN, "A1", "Мебель", "Ich putze jeden Samstag das Fenster."),

        # --- Еда ---
        ("essen", "есть (принимать пищу)", "aß", "gegessen", Auxiliary.HABEN, "A1", "Еда", "Ich esse jeden Tag Gemüse."),
        ("trinken", "пить", "trank", "getrunken", Auxiliary.HABEN, "A1", "Еда", "Die Kinder trinken Milch."),
        ("kochen", "готовить (на плите)", "kochte", "gekocht", Auxiliary.HABEN, "A1", "Еда", "Meine Mutter kocht eine Suppe."),
        ("backen", "печь, выпекать", "backte", "gebacken", Auxiliary.HABEN, "A1", "Еда", "Wir backen einen Kuchen."),
        ("schneiden", "резать", "schnitt", "geschnitten", Auxiliary.HABEN, "A1", "Еда", "Ich schneide das Brot."),
        ("probieren", "пробовать", "probierte", "probiert", Auxiliary.HABEN, "A1", "Еда", "Probier mal den Kuchen!"),

        # --- Семья ---
        ("lieben", "любить", "liebte", "geliebt", Auxiliary.HABEN, "A1", "Семья", "Ich liebe meine Familie sehr."),
        ("helfen", "помогать", "half", "geholfen", Auxiliary.HABEN, "A1", "Семья", "Ich helfe meiner Mutter in der Küche."),
        ("besuchen", "навещать, посещать", "besuchte", "besucht", Auxiliary.HABEN, "A1", "Семья", "Wir besuchen die Großeltern am Wochenende."),
        ("wohnen", "жить, проживать", "wohnte", "gewohnt", Auxiliary.HABEN, "A1", "Семья", "Meine Familie wohnt in einem großen Haus."),
        ("heiraten", "жениться, выходить замуж", "heiratete", "geheiratet", Auxiliary.HABEN, "A2", "Семья", "Sie wollen nächstes Jahr heiraten."),

        # --- Движение ---
        ("gehen", "идти, ходить", "ging", "gegangen", Auxiliary.SEIN, "A1", "Движение", "Ich gehe jeden Morgen zur Arbeit."),
        ("kommen", "приходить, приезжать", "kam", "gekommen", Auxiliary.SEIN, "A1", "Движение", "Wann kommst du nach Hause?"),
        ("fahren", "ехать (транспортом)", "fuhr", "gefahren", Auxiliary.SEIN, "A1", "Движение", "Ich fahre mit dem Zug nach Berlin."),
        ("laufen", "бежать, идти пешком", "lief", "gelaufen", Auxiliary.SEIN, "A1", "Движение", "Ich laufe jeden Tag im Park."),
        ("fliegen", "лететь", "flog", "geflogen", Auxiliary.SEIN, "A1", "Движение", "Das Flugzeug fliegt nach London."),
        ("schwimmen", "плавать", "schwamm", "geschwommen", Auxiliary.SEIN, "A1", "Движение", "Die Kinder schwimmen im See."),
        ("springen", "прыгать", "sprang", "gesprungen", Auxiliary.SEIN, "A1", "Движение", "Das Kind springt über die Pfütze."),
        ("tanzen", "танцевать", "tanzte", "getanzt", Auxiliary.HABEN, "A1", "Движение", "Wir tanzen gerne auf Partys."),
        ("warten", "ждать", "wartete", "gewartet", Auxiliary.HABEN, "A1", "Движение", "Ich warte auf den Bus."),
        ("bringen", "приносить, привозить", "brachte", "gebracht", Auxiliary.HABEN, "A1", "Движение", "Kannst du mir das Buch bringen?"),

        # --- Время ---
        ("beginnen", "начинаться, начинать", "begann", "begonnen", Auxiliary.HABEN, "A1", "Время", "Der Unterricht beginnt um acht Uhr."),
        ("enden", "заканчиваться", "endete", "geendet", Auxiliary.HABEN, "A1", "Время", "Der Film endet um zehn Uhr."),
        ("dauern", "длиться, продолжаться", "dauerte", "gedauert", Auxiliary.HABEN, "A1", "Время", "Die Reise dauert zwei Stunden."),
        ("schlafen", "спать", "schlief", "geschlafen", Auxiliary.HABEN, "A1", "Время", "Ich schlafe acht Stunden pro Nacht."),
        ("aufstehen", "вставать (с постели)", "stand auf", "aufgestanden", Auxiliary.SEIN, "A1", "Время", "Kinder müssen früh aufstehen."),
        ("frühstücken", "завтракать", "frühstückte", "gefrühstückt", Auxiliary.HABEN, "A1", "Время", "Wir frühstücken zusammen um acht."),
        ("warten", "ждать", "wartete", "gewartet", Auxiliary.HABEN, "A1", "Время", "Warte bitte einen Moment."),
    ]

    print("Seeding nouns...")
    noun_count = 0
    for german, translation, gender, plural, level, category, example in nouns:
        word = Word(
            german=german,
            translation=translation,
            word_type=WordType.NOUN,
            level=level,
            category=category,
            example_sentence=example,
        )
        db.add(word)
        db.flush()

        detail = NounDetail(
            word_id=word.id,
            gender=gender,
            plural=plural,
        )
        db.add(detail)
        noun_count += 1

    print("Seeding verbs...")
    verb_count = 0
    for german, translation, praeteritum, perfekt, auxiliary, level, category, example in verbs:
        word = Word(
            german=german,
            translation=translation,
            word_type=WordType.VERB,
            level=level,
            category=category,
            example_sentence=example,
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
        verb_count += 1

    db.commit()
    total = noun_count + verb_count
    print(f"\n✅ Successfully seeded {total} words!")
    print(f"   - Nouns: {noun_count}")
    print(f"   - Verbs: {verb_count}")
    print("Categories: Мебель, Еда, Семья, Движение, Время")
    print("All words have example_sentence (important for fill_blank tasks).")
    db.close()


if __name__ == "__main__":
    seed_expanded()
