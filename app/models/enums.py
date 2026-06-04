import enum


class WordType(str, enum.Enum):
    NOUN = "noun"
    VERB = "verb"


class Gender(str, enum.Enum):
    DER = "der"
    DIE = "die"
    DAS = "das"


class Auxiliary(str, enum.Enum):
    HABEN = "haben"
    SEIN = "sein"
