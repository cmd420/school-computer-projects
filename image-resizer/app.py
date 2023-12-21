from io import BytesIO
from pathlib import Path
from PIL import Image, ImageFilter
from cache_invalidation import CacheInvalidator
from flask import Flask, render_template, request, send_from_directory, send_file


STATIC_FOLDER = './static'
TEMPLATES_FOLDER = './templates'
IMAGES_FOLDER = Path(STATIC_FOLDER) / 'images'
IMAGES_URL = 'http://localhost:1984/images/'
app = Flask(__name__, template_folder=TEMPLATES_FOLDER, static_folder=STATIC_FOLDER)
invalidator = CacheInvalidator('./static/images', 1)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html')
    elif request.method == 'POST':
        file = request.files['file']
        if not file:
            return render_template('index.html', error='You must upload a file.')
        
        image_path = IMAGES_FOLDER / file.filename
        file.save(image_path)
        invalidator.update(str(image_path))
        
        return render_template('resize.html', image_url=IMAGES_URL + file.filename)
    else:
        return 'Method not supported'
    
@app.get('/images/<filename>')
def get_image(filename: str):
    height = request.args.get('height')
    width = request.args.get('width')
    print(height, width)

    if not height and not width:
        return send_from_directory(IMAGES_FOLDER, filename)
    try:
        if height:
            height = int(height)
        if width:
            width = int(width)
    except:
        return 'Invalid size parameters.', 400
    
    image_path = IMAGES_FOLDER / filename
    if not image_path.exists():
        return 'Not found.', 404
    
    image = Image.open(image_path).convert('RGB')
    resized_image = image.resize((width or image.width, height or image.height))

    img_io = BytesIO()
    resized_image.save(img_io, 'JPEG', quality=100)
    img_io.seek(0, 0)

    invalidator.update(str(image_path))
    return send_file(img_io, mimetype='image/jpeg')


if __name__ == '__main__':
    # invalidator.start()
    try:
        app.run('localhost' , 1984, True)
    except:
        pass
        # invalidator.stop()