from flask import Flask, render_template, send_file, url_for, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import secrets
import string
import qrcode
import os

app = Flask(__name__)

db = SQLAlchemy()

class Link(db.Model):
    id = db.Column(db.String(16), primary_key=True)
    text = db.Column(db.String(500), nullable=False)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///link.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    db.create_all()

IMAGE_FOLDER = "static/Images/"
SERVER_URL = "localhost:5000"
DEBUG = True

# to be accessed from PC
@app.route('/', methods = ['GET'])
def home():
    alphabet = string.ascii_letters + string.digits
    thefuckingcode = ''.join(secrets.choice(alphabet) for i in range(16))
    link_url = SERVER_URL + url_for('link', thefuckingcodeis=thefuckingcode)
    check_link_url = SERVER_URL + url_for('check_link', thefuckingcode=thefuckingcode)
    # Create a QR code instance and add the random string as data
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(link_url)
    # Compile the QR code and save it to a file
    qr.make(fit=True)
    image_name = thefuckingcode+".png"
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(IMAGE_FOLDER+image_name)
    app.logger.debug("continue on this url: "+link_url)
    # generate url to get accessed from template
    image_url = url_for('show_image', image_name=image_name)
    return render_template("./index.html", image_url=image_url, thefuckingcode=thefuckingcode, debug=DEBUG)

# to be accessed from Mobile
@app.route('/link/', methods = ['GET','POST'])
def link():
    if request.method == 'GET':
        thefuckingcode = request.args.get('thefuckingcodeis')
        app.logger.debug(thefuckingcode)
        return render_template("./link.html", thefuckingcode=thefuckingcode)
    elif request.method == 'POST':
        thefuckingcode = request.form.get('thefuckingcode')
        thefuckinglink = request.form.get('thefuckinglink')
        app.logger.debug(thefuckingcode)
        app.logger.debug(thefuckinglink)
        #store value in DB
        new_link = Link(id=thefuckingcode, text=thefuckinglink)
        db.session.add(new_link)
        db.session.commit()

        return "cool, thanks idiot. you can close this tab"
    else:
        return request.method + " method not supported, only use GET or POST"

# returns thefuckinglink if loaded
@app.route('/check-link/', methods = ['GET'])
def check_link():
    thefuckingcode = request.args.get('thefuckingcode')
    app.logger.debug(thefuckingcode)
    if thefuckingcode == "":
        return ""
    links = Link.query.all()
    for link in links:
        app.logger.debug(link.id)
        if link.id == thefuckingcode:
            return jsonify({'text':link.text})
    return jsonify({})

# add endpoint to delete qr file and entry from db
@app.route('/delete-link/', methods = ['POST'])
def delete_link():
    req_data = request.get_json()
    thefuckingcode = req_data['thefuckingcode']
    app.logger.debug(thefuckingcode)
    if thefuckingcode == "":
        return ""
    links = Link.query.all()
    for link in links:
        if link.id == thefuckingcode:
            db.session.delete(link)
            db.session.commit()
            os.remove(IMAGE_FOLDER+thefuckingcode+".jpg")
            return

# receives a request to load an image
@app.route('/image/', methods = ['GET'])
def show_image():
    image_name = request.args.get('image_name')
    app.logger.debug(image_name)
    return send_file(IMAGE_FOLDER+image_name, mimetype='image/jpeg')

# ONLY DEBUG. Deletes all the entries in the DB
@app.route('/delete-all/', methods = ['POST'])
def delete_all():
    if not DEBUG:
        return
    links = Link.query.all()
    for link in links:
        db.session.delete(link)
        db.session.commit()
    return jsonify({})

if __name__ == '__main__':
    app.run(debug=DEBUG)
