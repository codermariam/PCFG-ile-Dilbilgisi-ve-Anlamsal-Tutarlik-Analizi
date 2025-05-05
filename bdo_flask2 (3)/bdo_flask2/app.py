from flask import Flask, render_template, request
from sentence_analyzer import SentenceAnalyzer, SemanticChecker

app = Flask(__name__)
analyzer = SentenceAnalyzer()
semantic_checker = SemanticChecker()

@app.route("/", methods=["GET"])
def home():
    return render_template("form.html")

@app.route("/analyze", methods=["POST"])
def analyze_sentence():
    user_input = request.form["user_input"].strip()

    parses = analyzer.analyze(user_input)

    if not parses:
        result = "❌ Cümle gramer açısından geçersiz."
        detail = "ℹ️ Beklenen yapı: (the + [sıfat] + isim + fiil) veya (zamir + fiil)"
        return render_template("form.html", result=result, detail=detail)

    try:
        parse_tree = parses[0]
        noun, verb = analyzer.extract_subject_and_verb(parse_tree)
    except Exception as e:
        result = "⚠ Bir hata oluştu."
        detail = str(e)
        return render_template("form.html", result=result, detail=detail)

    if noun is None or verb is None:
        result = "⚠ Anlamsal analiz için yeterli bilgi bulunamadı."
        return render_template("form.html", result=result)

    score = semantic_checker.semantic_score(noun, verb)
    risk = semantic_checker.risk_level(score)

    result = "✅ Cümle gramer açısından geçerli."
    detail = f"🔍 Bulunan Özne: {noun}, Fiil: {verb} | 📈 Anlamsal Skor: {int(score * 100)}% | 🚦 Risk Seviyesi: {risk}"

    if risk == "High Risk":
        hallucination_warning = "🚨 Bu cümlede hallüsinasyon riski VAR!"
    elif risk == "Medium Risk":
        hallucination_warning = "⚠️ Bu cümlede orta seviyede hallüsinasyon riski bulunuyor."
    else:
        hallucination_warning = "✅ Cümlede hallüsinasyon riski tespit edilmedi."

    return render_template("form.html", result=result, detail=detail, hallucination_warning=hallucination_warning)

if __name__ == "__main__":
    app.run(debug=True)
