from flask import Blueprint, render_template, request, session, redirect, url_for
import requests
from utils import login_required

bp = Blueprint('devinetteSansAlcool', __name__)

@bp.route('/devinette-sans-alcool', methods=['GET', 'POST'])
@login_required
def devinette_sans_alcool():
    if request.method == 'POST':
        return handle_post_request()

    drink = fetch_non_alcoholic_cocktail()
    if not drink:
        return "Erreur : aucun cocktail sans alcool trouvé", 500

    cocktail_name = drink.get("strDrink")
    ingredients = extract_ingredients_with_measures(drink)

    session.update({
        'cocktail_non_alcool': cocktail_name,
        'ingredients_non_alcool': ingredients
    })

    return render_template('devinetteSansAlcool.html', ingredients=ingredients)


# ---------- FONCTIONS UTILITAIRES ----------

def fetch_non_alcoholic_cocktail():
    """Récupère un cocktail sans alcool depuis l’API."""
    try:
        url = "https://www.thecocktaildb.com/api/json/v1/1/random.php?c=Non_Alcoholic"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        drinks = data.get("drinks")
        return drinks[0] if drinks else None
    except requests.RequestException:
        return None


def extract_ingredients_with_measures(drink):
    """Extrait les ingrédients avec leurs quantités."""
    ingredients = []
    for i in range(1, 16):
        ingredient = drink.get(f"strIngredient{i}")
        measure = drink.get(f"strMeasure{i}")
        if ingredient:
            formatted = f"{measure.strip()} {ingredient.strip()}" if measure else ingredient.strip()
            ingredients.append(formatted)
    return ingredients


def handle_post_request():
    """Gère la vérification de la réponse utilisateur."""
    user_guess = request.form.get('ingredient', '').strip()
    cocktail_name = session.get('cocktail_non_alcool')

    if not cocktail_name:
        return redirect(url_for('devinette.devinette_sans_alcool'))

    result = (
        "Bonne réponse !" if user_guess.lower() == cocktail_name.lower()
        else f"Mauvaise réponse ! Le cocktail était : {cocktail_name}"
    )

    return render_template(
        'devinetteSansAlcool.html',
        ingredients=session.get('ingredients_non_alcool', []),
        result=result
    )
