from flask import Flask, request, jsonify, send_file
from werkzeug.utils import secure_filename
from cryptography.fernet import Fernet
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

# Generowanie klucza szyfrowania
def generate_key():
    return Fernet.generate_key()

# Zapisywanie klucza do pliku
def save_key(key, filename):
    with open(filename, 'wb') as key_file:
        key_file.write(key)

# Odczytywanie klucza z pliku
def load_key(filename):
    with open(filename, 'rb') as key_file:
        return key_file.read()

# Szyfrowanie pliku
def encrypt_file(key, input_file, output_file):
    cipher = Fernet(key)
    with open(input_file, 'rb') as file:
        data = file.read()
        encrypted_data = cipher.encrypt(data)
        with open(output_file, 'wb') as encrypted_file:
            encrypted_file.write(encrypted_data)

# Deszyfrowanie pliku
def decrypt_file(key, input_file, output_file):
    cipher = Fernet(key)
    with open(input_file, 'rb') as file:
        encrypted_data = file.read()
        decrypted_data = cipher.decrypt(encrypted_data)
        with open(output_file, 'wb') as decrypted_file:
            decrypted_file.write(decrypted_data)

# Endpoint dla wrzucania pliku i zaszyfrowania
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    key = generate_key()
    save_key(key, 'encryption_key.key')
    encrypted_filename = secure_filename(file.filename) + '.enc'
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], encrypted_filename))

    encrypt_file(key, os.path.join(app.config['UPLOAD_FOLDER'], encrypted_filename), os.path.join(app.config['UPLOAD_FOLDER'], encrypted_filename))

    return jsonify({'message': 'File uploaded and encrypted successfully'}), 200

# Endpoint do ściągania i odszyfrowywania pliku
@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    key = load_key('encryption_key.key')
    encrypted_file = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    decrypted_filename = secure_filename(filename)[:-4]  # Usunięcie '.enc' z nazwy pliku
    decrypted_file = os.path.join(app.config['UPLOAD_FOLDER'], decrypted_filename)

    decrypt_file(key, encrypted_file, decrypted_file)

    return send_file(decrypted_file, as_attachment=True, attachment_filename=decrypted_filename)

if __name__ == '__main__':
    app.run()
