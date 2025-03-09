from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from werkzeug.utils import secure_filename
import os
import subprocess
from pathlib import Path

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for flash messages

# Configure upload folders
UPLOAD_FOLDER = Path('Input')
ENCRYPTED_FOLDER = Path('Encrypted')
CONFUSION_FOLDER = Path('Confusion')
DECRYPTED_FOLDER = Path('Decrypted')

# Ensure all required directories exist
for folder in [UPLOAD_FOLDER, ENCRYPTED_FOLDER, CONFUSION_FOLDER, DECRYPTED_FOLDER]:
    folder.mkdir(exist_ok=True)

# Configure allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    # Get list of original, encrypted and decrypted images
    original_images = [f for f in os.listdir(UPLOAD_FOLDER) if allowed_file(f)]
    encrypted_images = [f for f in os.listdir(ENCRYPTED_FOLDER) if allowed_file(f)]
    decrypted_images = [f for f in os.listdir(DECRYPTED_FOLDER) if allowed_file(f)]
    
    return render_template('index.html', 
                           original_images=original_images,
                           encrypted_images=encrypted_images,
                           decrypted_images=decrypted_images)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    
    file = request.files['file']
    
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        flash(f'File {filename} uploaded successfully!')
        return redirect(url_for('index'))
    
    flash('Invalid file type. Only images are allowed.')
    return redirect(url_for('index'))

@app.route('/encrypt', methods=['POST'])
def encrypt_image():
    filename = request.form.get('filename')
    beta = request.form.get('beta')
    
    if not filename or not beta:
        flash('Please select an image and provide a beta value')
        return redirect(url_for('index'))
    
    try:
        beta_value = int(beta)
        # Fix: Pass the beta value correctly to the subprocess
        result = subprocess.run(['python', 'encryption.py', filename, str(beta_value)], 
                               capture_output=True, 
                               text=True)
        
        if result.returncode == 0:
            flash(f'Image {filename} encrypted successfully!')
        else:
            flash(f'Error encrypting image: {result.stderr}')
    except ValueError:
        flash('Beta must be an integer value')
    except Exception as e:
        flash(f'Error: {str(e)}')
    
    return redirect(url_for('index'))

@app.route('/decrypt', methods=['POST'])
def decrypt_image():
    filename = request.form.get('filename')
    
    if not filename:
        flash('Please select an image to decrypt')
        return redirect(url_for('index'))
    
    try:
        # Run the decryption script
        result = subprocess.run(['python', 'decryption.py', filename], 
                                capture_output=True, 
                                text=True)
        
        if result.returncode == 0:
            flash(f'Image {filename} decrypted successfully!')
        else:
            flash(f'Error decrypting image: {result.stderr}')
    except Exception as e:
        flash(f'Error: {str(e)}')
    
    return redirect(url_for('index'))

@app.route('/images/<folder>/<filename>')
def serve_image(folder, filename):
    folder_map = {
        'input': UPLOAD_FOLDER,
        'encrypted': ENCRYPTED_FOLDER,
        'confusion': CONFUSION_FOLDER,
        'decrypted': DECRYPTED_FOLDER
    }
    
    return send_from_directory(folder_map.get(folder, UPLOAD_FOLDER), filename)

if __name__ == '__main__':
    app.run(debug=True)
