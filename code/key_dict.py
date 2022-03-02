import spacy

nlp = spacy.load(
    "en_core_web_sm", disable=["ner", "parser"]
)  # needed to avoid errors with phrase patterns

# Belief speaking keywords and patterns
belief_keywords = {
    "verbs": [
        "believe",
        "confide",
        "consider",
        "envisage",
        "feel",
        "guess",
        "know",
        "observe",
        "presume",
        "regret",
        "suppose",
        "think",
        "trust",
        "view",
    ],
    "nouns": [
        "guess",
        "intuition",
        "opinion",
        "position",
        "sensation",
        "sentiment",
        "suggestion",
        "trust",
        "view",
    ],
    "adjectives": [
        "doubtless",
        "firsthand",
        "obvious",
        "simple",
        "straightforward",
    ],
    "adverbs": [
        "admittedly",
        "basically",
        "certainly",
        "clearly",
        "definitely",
        "frankly",
        "honestly",
        "indeed",
        "obviously",
        "plainly",
        "probably",
        "really",
        "surely",
        "truly",
        "undoubtedly",
    ],
    "phrases": ["no doubt", "of course", "safe to"],
}

belief_patterns = {
    "verbs": [
        [{"LOWER": {"IN": ["I", "we"]}}, {"LEMMA": verb, "POS": "VERB"}]
        for verb in belief_keywords["verbs"]
    ],
    "nouns": [
        [{"LOWER": {"IN": ["my", "our"]}}, {"LEMMA": noun, "POS": "NOUN"}]
        for noun in belief_keywords["nouns"]
    ],
    "adverbs": [[{"LOWER": adverb}] for adverb in belief_keywords["adverbs"]],
    "adjectives": [
        [{"LEMMA": adjective}] for adjective in belief_keywords["adjectives"]
    ],
    "sure": [
        [
            {"LOWER": {"IN": ["make", "made", "makes", "making", "be"]}, "OP": "!"},
            {"LOWER": "sure"},
        ]
    ],
    "phrases": [nlp(phrase) for phrase in belief_keywords["phrases"]],
}


# Truth seeking keywords and patterns
truth_keywords = {
    "verbs": [
        "analyze",
        "assert",
        "assess",
        "claim",
        "contemplate",
        "correct",
        "debunk",
        "determine",
        "estimate",
        "evaluate",
        "examine",
        "explore",
        "fact-check",
        "find",
        "inspect",
        "investigate",
        "judge",
        "overhaul",
        "ponder",
        "prove",
        "question",
        "quiz",
        "rate",
        "rectify",
        "research",
        "revise",
        "sample",
        "scrutinize",
        "search",
        "signal",
        "specify",
        "suggest",
        "supervise",
        "test",
        "trace",
        "track",
        "try",
        "validate",
        "verify",
        "reflect",
        "testimony",
        "witness",
    ],
    "nouns": [
        "assertion",
        "claim",
        "contention",
        "correction",
        "estimate",
        "evidence",
        "exploration",
        "fact",
        "fact-check",
        "hint",
        "improvement",
        "information",
        "look",
        "proof",
        "question",
        "rate",
        "reality",
        "research",
        "sample",
        "science",
        "search",
        "signal",
        "test",
        "trace",
        "track",
        "trial",
        "truth",
        "testimony",
    ],
    "adjectives": ["correct", "real", "tentative"],
    "adverbs": ["actually", "genuinely", "virtually"],
}

truth_patterns = {
    "verbs": [
        [{"LOWER": {"IN": ["I", "we"]}}, {"LEMMA": verb, "POS": "VERB"}]
        for verb in truth_keywords["verbs"]
    ],
    "look": [[{"LEMMA": "look", "POS": "VERB"}, {"LOWER": "forward", "OP": "!"}]],
    "nouns": [[{"LEMMA": noun, "POS": "NOUN"}] for noun in truth_keywords["nouns"]],
    "adverbs": [[{"LOWER": adverb}] for adverb in truth_keywords["adverbs"]],
    "adjectives": [
        [{"LEMMA": adjective}] for adjective in truth_keywords["adjectives"]
    ],
}


# Keywords and patterns for fostering understanding behaviour
foster_keywords = {
    "verbs": [
        "acknowledge",
        "admit",
        "affirm",
        "agree",
        "appreciate",
        "approve",
        "argue",
        "ask",
        "assure",
        "certify",
        "concede",
        "confirm",
        "consent",
        "consider",
        "convey",
        "convince",
        "declare",
        "deem",
        "demonstrate",
        "discover",
        "discuss",
        "dispute",
        "endorse",
        "exhibit",
        "explain",
        "expose",
        "gather",
        "illustrate",
        "indicate",
        "induce",
        "inform",
        "interpret",
        "introduce",
        "learn",
        "manifest",
        "notice",
        "observe",
        "perceive",
        "persuade",
        "point",
        "realize",
        "reason",
        "recognize",
        "reveal",
        "say",
        "show",
        "state",
        "tell",
        "think",
        "tolerate",
        "uncover",
        "understand",
        "unfold",
        "unveil",
        "warn",
    ],
    "nouns": ["assent", "discover", "dispute", "point", "reason"],
    "phrases": [
        "find out",
        "hand over",
        "learn of",
        "pay attention to",
        "take note",
        "think about",
    ],
}

foster_patterns = {
    "verbs": [[{"LEMMA": verb, "POS": "VERB"}] for verb in foster_keywords["verbs"]],
    "nouns": [[{"LEMMA": noun, "POS": "NOUN"}] for noun in foster_keywords["nouns"]],
    "phrases": [nlp(phrase) for phrase in foster_keywords["phrases"]],
}
