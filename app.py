import os

from dotenv import load_dotenv
from flask import Flask, flash, request, redirect, url_for, render_template

from steganography import encrypt, decrypt

load_dotenv()


app = Flask(__name__)
app.secret_key = "cairocoders-endnalan"
app.config['UPLOAD_FOLDER'] = os.getenv("UPLOAD_FOLDER")
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024


def allowed_file(filename: str) -> bool:
    """ Determines whether the file extension in parameter is one of the allowed file extensions. """
    return ('.' in filename and filename.rsplit('.', 1)[1].lower() in
            set(os.getenv("ALLOWED_EXTENSIONS").split(",")))


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/', methods=['POST'])
def upload_image():
    """ Route for upload an image and the text to be hidden  """
    message = request.form['mes']

    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)

    file = request.files['file']
    if file.filename == '':
        flash('No image selected for uploading')
        return redirect(request.url)

    if file and allowed_file(file.filename):
        # Save file
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
        filename = file.filename

        result = encrypt(image=os.path.join(app.config['UPLOAD_FOLDER'], file.filename), text=message)

        if result:
            new_filename = os.path.join(app.config['UPLOAD_FOLDER'], f"{filename.split('.')[0]}{os.getenv('FILE_EXT')}")
            result.save(new_filename)
            flash('Image successfully upload and displayed below this alert')
            return render_template('index.html', filename=new_filename, msg=message)
        else:
            flash('Image error')
            return redirect(request.url)
    else:
        flash('Allowed images types are only png')
        return redirect(request.url)


@app.route('/decode')
def decode():
    return render_template('decode.html')


@app.route('/decode', methods=['POST'])
def decode_image():
    """ Route to load an image to extract hidden information """
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)

    file = request.files['file']
    if file.filename == '':
        flash('No image selected for uploading')
        return redirect(request.url)

    if file and allowed_file(file.filename):
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
        filename = file.filename

        hidden_message = decrypt(image=os.path.join(app.config['UPLOAD_FOLDER'], file.filename))

        if hidden_message:
            flash(f'Text successfully detected: { hidden_message }')
            return render_template('/decode.html', filename=filename)
        else:
            flash('Image error')
            return redirect(request.url)
    else:
        flash('Allowed images types are only png')
        return redirect(request.url)


@app.route('/display/<filename>')
def display_image(filename):
    return redirect(url_for('static', filename=f'/uploads/{filename}'), code=301)


@app.route('/<filename>')
def display_decode_image(filename):
    return redirect(url_for('static', filename=f'/uploads/{filename}'), code=301)


if __name__ == "__main__":
    app.run(host=os.getenv("HOST"), port=int(os.getenv("PORT")))
