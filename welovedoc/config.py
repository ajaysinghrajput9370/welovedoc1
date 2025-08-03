import os

class Config:
    SECRET_KEY = 'your-secret-key-here'  # Change this!
    UPLOAD_FOLDER = 'uploads'
    OUTPUT_FOLDER = 'output'
    DATABASE = 'database.db'
    ALLOWED_EXTENSIONS = {'pdf', 'xlsx', 'xls'}
    
    # Razorpay config (replace with your keys)
    RAZORPAY_KEY_ID = 'rzp_test_your_key'
    RAZORPAY_KEY_SECRET = 'your_secret_key'

    @staticmethod
    def init_app(app):
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])
        if not os.path.exists(app.config['OUTPUT_FOLDER']):
            os.makedirs(app.config['OUTPUT_FOLDER'])