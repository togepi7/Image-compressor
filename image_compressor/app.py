from flask import Flask, render_template, request, send_file, abort
from PIL import Image
import io

app = Flask(__name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'bmp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def compress_image_to_size(image, target_size_kb, min_quality=1, max_quality=95):
    original_format = image.format
    if original_format == 'JPEG':
        original_format = 'JPG'  # Normalize JPEG to JPG
    
    quality = max_quality
    step = 5
    best_quality = None
    best_size = float('inf')
    best_output = None
    
    while quality >= min_quality:
        output = io.BytesIO()
        if original_format in ['PNG', 'WEBP']:
            image.save(output, format=original_format, optimize=True)
        elif original_format == 'BMP':
            # BMP doesn't support quality, so we'll convert to PNG for compression
            image.save(output, format='PNG', optimize=True)
            original_format = 'PNG'
        else:  # JPG and other formats
            image.save(output, format='JPEG', quality=quality)
        
        size = output.tell() / 1024  # Size in KB
        
        if size <= target_size_kb and (best_quality is None or quality > best_quality):
            best_quality = quality
            best_size = size
            best_output = output
        
        if size > target_size_kb:
            quality -= step
        else:
            if step > 1:
                quality += step
                step = max(1, step // 2)
            else:
                break
    
    if best_output is None:
        # If we couldn't meet the target size, return the smallest version
        best_output = output
        best_size = size
    
    best_output.seek(0)
    return best_output, best_size, original_format

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/compress', methods=['POST'])
def compress_image():
    if 'image' not in request.files:
        abort(400, description="No image file provided")
    
    image_file = request.files['image']
    
    if image_file.filename == '':
        abort(400, description="No selected file")
    
    if not allowed_file(image_file.filename):
        abort(400, description="File type not allowed. Supported formats are: " + ", ".join(ALLOWED_EXTENSIONS))
    
    try:
        target_size_kb = int(request.form['size'])
        image = Image.open(image_file)
        compressed_image, final_size, format = compress_image_to_size(image, target_size_kb)
    except ValueError:
        abort(400, description="Invalid target size. Please enter a valid number.")
    except IOError:
        abort(400, description="Unable to open image file. File may be corrupted or in an unsupported format.")

    return send_file(compressed_image, mimetype=f'image/{format.lower()}', 
                     as_attachment=True, download_name=f'compressed_{final_size:.1f}KB.{format.lower()}')

if __name__ == '__main__':
     app.run(debug=True)
