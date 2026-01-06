from flask import Blueprint, render_template, request, session, redirect, url_for
import requests
from utils import add_win

bp = Blueprint('devinette', __name__, url_prefix='/devinette')

# -------- Route principale : deviner le cocktail --------
@bp.route('/', methods=['GET', 'POST'])
def jeu_devinette():
    """Jeu : deviner les ingrédients d'un cocktail mystère"""
    if request.method == 'POST' and request.form.get('reset'):
        return reset_devinette()

    game: dict = get_or_create_game()

    message = None
    if request.method == 'POST' and not request.form.get('reset'):
        message = handle_user_guess(game)

    return render_template(
        "devinette_cocktail.html",
        cocktail_name=game.get('cocktail', ''),
        cocktail_image=game.get('img', ''),
        ingredients=game.get('ingredients', []),
        attempts=game.get('attempts', []),
        message=message
    )


# ---------- Fonctions utilitaires ----------

def reset_devinette():
    session.pop('devinette', None)
    return redirect(url_for('devinette.jeu_devinette'))


def get_or_create_game():
    """Récupère le jeu existant ou crée un nouveau cocktail mystère"""
    if 'devinette' not in session:
        cocktail_data = fetch_random_cocktail()
        if not cocktail_data:
            return "Erreur : impossible de récupérer un cocktail", 500

        ingredients = extract_ingredients(cocktail_data)
        session['devinette'] = {
            'cocktail': cocktail_data['strDrink'],
            'ingredients': ingredients,
            'img': cocktail_data['strDrinkThumb'],
            'attempts': [],
            'win': False
        }
    return session['devinette']


def fetch_random_cocktail():
    try:
        resp = requests.get("https://www.thecocktaildb.com/api/json/v1/1/random.php", timeout=5)
        resp.raise_for_status()
        drinks = resp.json().get('drinks')
        return drinks[0] if drinks else None
    except requests.RequestException:
        return None


def extract_ingredients(data):
    return [
        data.get(f"strIngredient{i}").strip().lower()
        for i in range(1, 16)
        if data.get(f"strIngredient{i}")
    ]


def handle_user_guess(game):
    """Traite la proposition utilisateur"""
    user_input = request.form.get('ingredient', '').strip()
    if not user_input:
        return None

    proposed = [x.strip().lower() for x in user_input.split(',') if x.strip()]
    solution = game['ingredients']

    feedback = [get_feedback(ing, solution) for ing in proposed]

    user_img, user_ingredients = fetch_user_drink(user_input)
    compared = compare_with_solution(user_ingredients, solution)

    game['attempts'].append({
        'raw_input': user_input,
        'img': user_img,
        'ingredient_feedback': feedback,
        'user_ingredients': compared
    })

    message = None
    if has_won(game):
        add_win()
        game['win'] = True
        message = f"🎉 Bravo ! Tu as trouvé tous les ingrédients du cocktail « {game['cocktail']} » !"

    session['devinette'] = game
    return message


def get_feedback(ingredient, solution_ingredients):
    """Retourne le statut 'good', 'partial' ou 'wrong'"""
    try:
        exists = requests.get(f"https://www.thecocktaildb.com/api/json/v1/1/search.php?i={ingredient}", timeout=5).json().get("ingredients") is not None
    except requests.RequestException:
        exists = False

    if ingredient in solution_ingredients:
        status = 'good'
    elif exists:
        status = 'partial'
    else:
        status = 'wrong'

    return {'ingredient': ingredient, 'status': status}


def fetch_user_drink(user_input):
    """Récupère le cocktail saisi par l'utilisateur"""
    try:
        resp = requests.get(f"https://www.thecocktaildb.com/api/json/v1/1/search.php?s={user_input}", timeout=5)
        drinks = resp.json().get('drinks')
        if not drinks:
            return None, []

        drink = drinks[0]
        ingredients = extract_ingredients(drink)
        return drink.get('strDrinkThumb'), ingredients
    except requests.RequestException:
        return None, []


def compare_with_solution(user_ingredients, solution_ingredients):
    return [{'ingredient': ing, 'status': 'good' if ing in solution_ingredients else 'wrong'} for ing in user_ingredients]


def has_won(game):
    found = {
        fb['ingredient']
        for at in game['attempts']
        for fb in at['user_ingredients']
        if fb['status'] == 'good'
    }
    return all(ing in found for ing in game['ingredients']) and not game.get('win')


# -------- Jeu : deviner les ingrédients --------
@bp.route('/ingredient', methods=['GET', 'POST'])
def jeu_ingredient():
    """Jeu : deviner les ingrédients d'un cocktail mystère"""

    if request.method == 'POST' and request.form.get('reset'):
        return reset_ingredient_game()

    game: dict = get_or_create_ingredient_game()
    message = None

    if request.method == 'POST' and not request.form.get('reset'):
        message = handle_ingredient_guess(game)

    return render_template(
        "devinette_ingredient.html",
        cocktail=game.get('cocktail', ''),
        cocktail_image=game.get('img', ''),
        ingredients=game.get('ingredients', []),
        attempts=game.get('attempts', []),
        message=message
    )


# ---------- Fonctions utilitaires ----------

def reset_ingredient_game():
    """Réinitialise la session du jeu"""
    session.pop('ingredient_game', None)
    return redirect(url_for('devinette.jeu_ingredient'))


def get_or_create_ingredient_game() -> dict:
    """Récupère le jeu existant ou crée un nouveau cocktail mystère"""
    if 'ingredient_game' not in session:
        session['ingredient_game'] = {}

    game = session['ingredient_game']

    if not game.get('cocktail'):
        cocktail_data = fetch_random_cocktail()
        if not cocktail_data:
            return {}

        ingredients = extract_ingredients(cocktail_data)
        game.update({
            'cocktail': cocktail_data['strDrink'],
            'img': cocktail_data['strDrinkThumb'],
            'ingredients': ingredients,
            'attempts': [],
            'win': False
        })
        session['ingredient_game'] = game

    return game


def handle_ingredient_guess(game: dict):
    """Traite la proposition de l’utilisateur et met à jour le jeu"""
    user_input = request.form.get('ingredient', '').strip().lower()
    if not user_input:
        return None

    proposed_list = [x.strip() for x in user_input.split(',') if x.strip()]
    feedback = [get_ingredient_feedback(ing, game['ingredients']) for ing in proposed_list]

    game.setdefault('attempts', []).append({
        'raw_input': user_input,
        'img': game['img'],
        'user_ingredients': feedback
    })

    message = None
    if has_won(game):
        add_win()
        game['win'] = True
        message = f"🎉 Bravo ! Tu as trouvé tous les ingrédients du cocktail « {game['cocktail']} » !"

    session['ingredient_game'] = game
    return message


def get_ingredient_feedback(ingredient: str, valid_ingredients: list):
    """Retourne le statut et l’image d’un ingrédient proposé"""
    status = 'good' if ingredient in valid_ingredients else 'wrong'
    img = fetch_ingredient_image(ingredient)
    return {'ingredient': ingredient, 'status': status, 'img': img}


def fetch_ingredient_image(ingredient: str):
    """Récupère l’image d’un ingrédient si disponible"""
    try:
        data = requests.get(
            f"https://www.thecocktaildb.com/api/json/v1/1/search.php?i={ingredient}",
            timeout=5
        ).json()
        if data.get("ingredients"):
            name = data["ingredients"][0]["strIngredient"]
            return f"https://www.thecocktaildb.com/images/ingredients/{name}-Medium.png"
    except requests.RequestException:
        pass
    return None
