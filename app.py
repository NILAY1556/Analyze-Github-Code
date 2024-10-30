from flask import Flask, request, render_template_string
from flask_cors import cross_origin

from analyze import AnalyzeRepo

app = Flask(__name__)


@app.route("/", methods=["POST"])
@cross_origin()  # Avoid CORS errors
def process():
    data = request.get_json()
    openai_key = "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"
    currentPageLink = data.get("currentPageLink")

    try:
        # Call AnalyzeRepo and get detailed summary
        summary_generator = AnalyzeRepo(openai_key, currentPageLink)
        result = summary_generator.run()
        return render_template_string(result)
    except Exception as e:
        return str(e)


if __name__ == "__main__":
    app.run(debug=True, host="localhost", port=8000)
