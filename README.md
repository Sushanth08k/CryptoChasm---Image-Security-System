# CryptoChasm - Image Security System

CryptoChasm is a Flask-based web application that securely encrypts and decrypts images using a chaos-based cryptographic algorithm. The system implements a confusion-diffusion architecture with Henon map and prime number generation for strong cryptographic security.

## Features

- **User-friendly web interface**: Upload, view, encrypt, and decrypt images through a simple browser interface
- **Two-phase encryption**: Implements both confusion and diffusion phases for robust encryption
- **Chaotic cryptography**: Uses chaotic maps and prime number theory for secure key generation
- **Flexible parameter control**: Customize encryption strength with beta parameter
- **Support for multiple image types**: Works with PNG, JPG, JPEG, GIF, and BMP files

## User Interface

The application provides a clean, intuitive interface with three main sections:

1. **Upload Image**: Select and upload new images to the system
2. **Original Images**: View uploaded images and encrypt them by providing a Beta parameter
3. **Encrypted Images**: View encrypted images and decrypt them with one click
4. **Decrypted Images**: View successfully decrypted images

![CryptoChasm UI](https://github.com/yourusername/cryptochasm/raw/main/docs/ui-example.png)

*Note: Replace the image URL with your actual screenshot location after uploading to your repository*

## Requirements

- Python 3.6+
- Flask
- Pillow (PIL)
- NumPy
- Werkzeug

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/cryptochasm.git
   cd cryptochasm
   ```

2. Install dependencies:
   ```
   pip install flask pillow numpy werkzeug
   ```

3. Create required directories (these will be created automatically if missing):
   - `Input`: For original images
   - `Confusion`: For confusion phase images
   - `Encrypted`: For encrypted images
   - `Decrypted`: For decrypted images

## Usage

1. Start the application:
   ```
   python app.py
   ```

2. Open your browser and navigate to `http://127.0.0.1:5000/`

3. Upload an image file (PNG, JPG, JPEG, GIF, or BMP)

4. To encrypt an image:
   - Select an image from the "Original Images" list
   - Enter a beta value (this is part of your encryption key)
   - Click "Encrypt"

5. To decrypt an image:
   - Select an image from the "Encrypted Images" list
   - Click "Decrypt" (uses the parameters stored in keys.txt)

## How It Works

### Encryption Algorithm

The encryption process consists of two phases:

1. **Confusion Phase**:
   - Shifts rows and columns of RGB color planes based on calculated vectors
   - Creates confusion by displacing pixels but retaining all original information

2. **Diffusion Phase**:
   - Implements chaotic Henon map generation based on alpha and beta parameters
   - XORs pixel values with the chaotic sequence to diffuse information

### Key Generation

- **Alpha**: Automatically calculated based on image characteristics
- **Beta**: User-provided parameter that affects encryption strength
- Both values are stored in `keys.txt` for decryption

## Security Considerations

- Keep your `keys.txt` file secure as it contains the decryption parameters
- Higher beta values generally result in stronger encryption
- The system uses a combination of chaotic maps and prime number theory for enhanced security

## Project Structure

- `app.py`: Flask web application
- `encryption.py`: Image encryption logic
- `decryption.py`: Image decryption logic
- `templates/index.html`: Web interface
- `keys.txt`: Store encryption/decryption parameters (generated during encryption)

## Future Improvements

- Add user authentication
- Implement secure key storage
- Support for additional file types
- Batch processing
- Performance optimizations for larger images

## License

[MIT License](LICENSE)

## Acknowledgments

- Based on chaos theory and cryptographic principles
- Implements confusion-diffusion architecture proposed by Claude Shannon
