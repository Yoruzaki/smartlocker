from flask import Flask, session
from database import init_db
from hardware import get_hardware

# Configuration
USE_MOCK_HARDWARE = True # Set to False for real Raspberry Pi

app = Flask(__name__)
app.secret_key = 'supersecretkey' # Change for production

# Translations
TRANSLATIONS = {
    'fr': {
        'title': 'Système de Casier Intelligent',
        'delivery': 'Livreur',
        'pickup': 'Client',
        'login_title': 'Connexion Livreur',
        'enter_pin': 'Entrez le PIN',
        'back': 'Retour',
        'pickup_title': 'Retrait Client',
        'enter_otp': 'Entrez le Code OTP',
        'select_locker': 'Sélectionnez un Casier',
        'logout': 'Déconnexion',
        'door_open': 'PORTE OUVERTE',
        'occupied': 'Occupé',
        'available': 'Disponible',
        'locker_opened': 'Casier Ouvert !',
        'generated_otp': 'Code OTP Généré :',
        'place_package': 'Veuillez déposer le colis et fermer la porte.',
        'take_package': 'Veuillez récupérer votre colis et fermer la porte.',
        'done': 'Terminé',
        'error': 'Erreur',
        'invalid_pin': 'PIN Invalide',
        'invalid_otp': 'OTP Invalide',
        'locker_not_found': 'Casier introuvable',
        'request_failed': 'Échec de la requête',
        'confirm_open': 'Ouvrir le casier',
        'already_occupied': 'Ce casier est déjà occupé !'
    },
    'ar': {
        'title': 'نظام الخزائن الذكية',
        'delivery': 'مندوب',
        'pickup': 'عميل',
        'login_title': 'تسجيل دخول المندوب',
        'enter_pin': 'أدخل الرمز السري',
        'back': 'رجوع',
        'pickup_title': 'استلام العميل',
        'enter_otp': 'أدخل رمز التحقق',
        'select_locker': 'اختر خزانة',
        'logout': 'خروج',
        'door_open': 'الباب مفتوح',
        'occupied': 'مشغول',
        'available': 'متاح',
        'locker_opened': 'تم فتح الخزانة!',
        'generated_otp': 'رمز التحقق الجديد:',
        'place_package': 'يرجى وضع الطرد وإغلاق الباب.',
        'take_package': 'يرجى أخذ الطرد وإغلاق الباب.',
        'done': 'تم',
        'error': 'خطأ',
        'invalid_pin': 'رمز خاطئ',
        'invalid_otp': 'رمز تحقق خاطئ',
        'locker_not_found': 'الخزانة غير موجودة',
        'request_failed': 'فشل الطلب',
        'confirm_open': 'فتح الخزانة',
        'already_occupied': 'هذه الخزانة مشغولة بالفعل!'
    }
}

@app.context_processor
def inject_conf_var():
    lang = session.get('lang', 'fr')
    return dict(lang=lang, t=TRANSLATIONS, dir='rtl' if lang == 'ar' else 'ltr')

# Initialize Hardware
hardware = get_hardware(use_mock=USE_MOCK_HARDWARE)

# Initialize Database
init_db()

# Import routes after app initialization to avoid circular imports
from routes import *

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
