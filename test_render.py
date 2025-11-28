from flask import Flask, render_template
import sqlite3

app = Flask(__name__)

@app.route('/index')
def index():
    return "Index"

@app.route('/set_language/<lang>', endpoint='set_language')
def set_language(lang):
    return "Language set"

@app.context_processor
def inject_conf_var():
    # Mock translations
    TRANSLATIONS = {
        'fr': {
            'title': 'Système de Casier Intelligent',
            'delivery': 'Livraison',
            'pickup': 'Retrait',
            'select_locker': 'Sélectionnez un Casier',
            'logout': 'Déconnexion',
            'door_open': 'PORTE OUVERTE',
            'occupied': 'Occupé',
            'available': 'Disponible',
            'locker_opened': 'Casier Ouvert !',
            'generated_otp': 'Code OTP Généré :',
            'place_package': 'Veuillez déposer le colis et fermer la porte.',
            'done': 'Terminé',
            'already_occupied': 'Occupé',
            'confirm_open': 'Ouvrir?',
            'error': 'Erreur',
            'request_failed': 'Echec'
        }
    }
    return dict(lang='fr', t=TRANSLATIONS, dir='ltr')

@app.route('/')
def test():
    # Mock data
    lockers = [
        {'id': 1, 'is_occupied': 0, 'door_closed': 1},
        {'id': 2, 'is_occupied': 1, 'door_closed': 1}
    ]
    hw_states = {1: True, 2: True}
    
    try:
        # Mock translations
        TRANSLATIONS = {
            'fr': {
                'title': 'Système de Casier Intelligent',
                'delivery': 'Livraison',
                'pickup': 'Retrait',
                'select_locker': 'Sélectionnez un Casier',
                'logout': 'Déconnexion',
                'door_open': 'PORTE OUVERTE',
                'occupied': 'Occupé',
                'available': 'Disponible',
                'locker_opened': 'Casier Ouvert !',
                'generated_otp': 'Code OTP Généré :',
                'place_package': 'Veuillez déposer le colis et fermer la porte.',
                'done': 'Terminé',
                'already_occupied': 'Occupé',
                'confirm_open': 'Ouvrir?',
                'error': 'Erreur',
                'request_failed': 'Echec'
            }
        }
        return render_template('delivery_dashboard.html', lockers=lockers, hw_states=hw_states, t=TRANSLATIONS, lang='fr', dir='ltr')
    except Exception as e:
        return str(e)

if __name__ == '__main__':
    app.run(debug=True, port=5003)
