from flask import Flask, render_template, request, send_file
import os
from excel_to_tally_xml import excel_to_tally_xml

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files["file"]
        if file:
            input_path = os.path.join(UPLOAD_FOLDER, file.filename)
            output_path = os.path.join(OUTPUT_FOLDER, "Generated_Tally_Ledger.xml")
            file.save(input_path)

            try:
                excel_to_tally_xml(input_path, output_path)
                return send_file(output_path, as_attachment=True)
            except Exception as e:
                return f"<h3 style='color:red;'>Error: {e}</h3>"

    return render_template("index.html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)

