from flask import Flask, render_template, request, jsonify
from backend import generate_recipe

app = Flask(__name__)


@app.route('/')
def home():
    return render_template("frontend.html")   # Flask will look inside /templates


@app.route('/process', methods=['POST'])
def process():
    payload = request.get_json() or {}
    dish = payload.get('dish')
    servings = payload.get('servings')

    if not dish or not servings:
        return jsonify({"error": "Missing 'dish' or 'servings' in request body"}), 400

    try:
        recipe = generate_recipe(dish, int(servings))
        return jsonify(recipe)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
