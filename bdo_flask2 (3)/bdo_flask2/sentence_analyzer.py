import nltk
from nltk import PCFG
from nltk.parse import pchart

# NLTK veri yolu ayarlanıyor
nltk.data.path = [
    r'C:\Users\USER\AppData\Roaming\nltk_data',
    *nltk.data.path
]

required_resources = {
    'punkt': 'tokenizers/punkt'
}

for resource_name, resource_path in required_resources.items():
    try:
        nltk.data.find(resource_path)
    except LookupError:
        nltk.download(resource_name, quiet=True)

def normalize_grammar(rules):
    normalized_rules = {}
    for lhs, productions in rules.items():
        total_prob = sum(prob for _, prob in productions)
        if total_prob == 0:
            raise ValueError(f"No probabilities provided for {lhs}")
        normalized_productions = [(rhs, prob / total_prob) for rhs, prob in productions]
        normalized_rules[lhs] = normalized_productions
    return normalized_rules

def generate_pcfg_string(normalized_rules):
    lines = []
    for lhs, productions in normalized_rules.items():
        for rhs, prob in productions:
            lines.append(f"{lhs} -> {rhs} [{prob:.4f}]")
    return '\n'.join(lines)

class SentenceAnalyzer:
    def __init__(self):
        self.grammar = self._build_grammar()
        self.parser = pchart.InsideChartParser(self.grammar)

    def _build_grammar(self):
        grammar_rules = {
            "S": [("NP VP", 1.0)],
            "NP": [("DT NN", 0.6), ("DT JJ NN", 0.2), ("PRP", 0.2)],
            "VP": [("VBZ", 0.5), ("VBD", 0.5)],
            "DT": [("'the'", 1.0)],
            "NN": [("'cat'", 0.3), ("'boy'", 0.3), ("'spaceship'", 0.4), ("'dog'", 0.4)],
            "VBZ": [("'runs'", 0.4), ("'flies'", 0.3), ("'barks'", 0.3)],
            "VBD": [("'barked'", 1.0)],
            "PRP": [("'he'", 0.5), ("'she'", 0.5)],
            "JJ": [("'big'", 0.5), ("'small'", 0.5)]
        }
        normalized = normalize_grammar(grammar_rules)
        pcfg_string = generate_pcfg_string(normalized)
        return PCFG.fromstring(pcfg_string)

    def analyze(self, sentence):
        tokens = sentence.lower().split()
        if not tokens:
            return []
        try:
            parses = list(self.parser.parse(tokens))
            return parses
        except Exception:
            return []

    def extract_subject_and_verb(self, parse_tree):
        noun = None
        verb = None

        for subtree in parse_tree.subtrees():
            if subtree.label() == 'NP':
                for leaf in subtree.leaves():
                    if leaf in {'cat', 'boy', 'spaceship', 'dog', 'he', 'she'}:
                        noun = leaf
            if subtree.label() == 'VP':
                for leaf in subtree.leaves():
                    if leaf in {'runs', 'flies', 'barks', 'barked'}:
                        verb = leaf
        return noun, verb

class SemanticChecker:
    def __init__(self):
        self.living_nouns = {'cat', 'boy', 'dog', 'he', 'she'}
        self.inanimate_nouns = {'spaceship'}

        self.actions_for_living = {'runs', 'barks', 'barked'}
        self.actions_for_inanimate = {'flies'}

    def semantic_score(self, noun, verb):
        if noun in self.living_nouns and verb in self.actions_for_living:
            return 1.0
        if noun in self.inanimate_nouns and verb in self.actions_for_inanimate:
            return 1.0
        if noun in self.inanimate_nouns and verb in self.actions_for_living:
            return 0.2
        if noun in self.living_nouns and verb in self.actions_for_inanimate:
            return 0.3
        return 0.0

    def risk_level(self, score):
        if score >= 0.8:
            return "Low Risk"
        elif 0.5 <= score < 0.8:
            return "Medium Risk"
        else:
            return "High Risk"

def main():
    analyzer = SentenceAnalyzer()
    semantic_checker = SemanticChecker()

    print("\n🧠 Grammar + Semantic Analyzer Ready!")
    print("Type a sentence to check. Type 'exit' to quit.\n")

    while True:
        sentence = input("Enter a sentence: ").strip()
        if sentence.lower() == 'exit':
            print("👋 Goodbye!")
            break

        parses = analyzer.analyze(sentence)

        if not parses:
            print("❌ Cümle gramer açısından geçersiz.")
            print("ℹ️ Beklenen yapı: (the + [sıfat] + isim + fiil) veya (zamir + fiil)\n")
            continue

        try:
            parse_tree = parses[0]
            noun, verb = analyzer.extract_subject_and_verb(parse_tree)
        except Exception as e:
            print(f"⚠ Bir hata oluştu: {str(e)}\n")
            continue

        if noun is None or verb is None:
            print("⚠ Anlamsal analiz için yeterli bilgi bulunamadı.\n")
            continue

        print("✅ Cümle gramer açısından geçerli.")
        print(f"🔍 Bulunan Özne: {noun}, Fiil: {verb}")

        score = semantic_checker.semantic_score(noun, verb)
        risk = semantic_checker.risk_level(score)

        print(f"📈 Anlamsal Tutarlılık Skoru: {int(score * 100)}%")
        print(f"🚦 Hallüsinasyon Riski Seviyesi: {risk}")

        if risk == "High Risk":
            print("🚨 Bu cümlede hallüsinasyon riski VAR!\n")
        elif risk == "Medium Risk":
            print("⚠️ Bu cümlede orta seviyede hallüsinasyon riski bulunuyor.\n")
        else:
            print("✅ Cümlede hallüsinasyon riski tespit edilmedi.\n")

if __name__ == "__main__":
    main()
