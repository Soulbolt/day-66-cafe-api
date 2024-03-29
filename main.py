from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from random import choice

app = Flask(__name__)

# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
db = SQLAlchemy()
db.init_app(app)


# Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):  # This is a dictionary comprehension function created inside the Cafe class definition. It will be used to turn rows into a dictionary before sending it to jsonify.
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/random")
def random():
    with app.app_context():
        response = db.session.execute(db.select(Cafe))
        all_cafe_places = response.scalars().all()
        randm_cafe = choice(all_cafe_places)
    return jsonify(cafe = {
        "id": randm_cafe.id,
        "name": randm_cafe.name,
        "map_url": randm_cafe.map_url,
        "img_url": randm_cafe.img_url,
        "location": randm_cafe.location,
        "seats": randm_cafe.seats,
        "has_toilet": randm_cafe.has_toilet,
        "has_wifi": randm_cafe.has_wifi,
        "has_sockets": randm_cafe.has_sockets,
        "can_take_calls": randm_cafe.can_take_calls,
        "coffee_price": randm_cafe.coffee_price
    })

# HTTP GET - Read Record
@app.route("/all")
def get_all_cafes():
    response = db.session.execute(db.select(Cafe).order_by(Cafe.name)).scalars().all()
    # all_cafe_locations = [cafe for cafe in response]
    return jsonify(cafes=[cafe.to_dict() for cafe in response])

@app.route("/search")
def search():
    loc = request.args.get("loc")
    cafe_list = db.session.execute(db.select(Cafe).where(Cafe.location == loc)).scalars().all()
    if cafe_list:
        return jsonify(cafes = [cafe.to_dict() for cafe in cafe_list])
    else:
        return jsonify(error = {
        "Not Found": "Sorry, we don't have a cafe at that location."
    }), 404

# HTTP POST - Create Record
@app.route("/add", methods=["POST"])
def add_cafe():
    new_cafe=Cafe(
        name=request.form.get("name"),
        map_url=request.form.get("map_url"),
        img_url=request.form.get("img_url"),
        location=request.form.get("location"),
        has_sockets=bool(request.form.get("has_sockets")),
        has_toilet=bool(request.form.get("has_toilet")),
        has_wifi=bool(request.form.get("has_wifi")),
        can_take_calls=bool(request.form.get("can_take_calls")),
        seats=request.form.get("seats"),
        coffee_price=request.form.get("coffee_price"),
    )
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(response = {
        "success": "Successfully added the new cafe."
    })

# HTTP PUT/PATCH - Update Record
@app.route("/update-price/<int:id>", methods=["PATCH"])
def update_price(id):
    new_price = request.args.get("new_price")
    price_to_update = db.get_or_404(Cafe, id)
    if price_to_update:
        price_to_update.coffee_price = new_price
        db.session.commit()
        return jsonify(success = {
            "success": "Successfully updated the price."
        })

# Handle bad request if ID does not exist to avoid 404 error that prevents for the if statement to be reached when using patch request
@app.errorhandler(404)
def invalid_route(e):
    return jsonify(error = {
        "Not Found": "Sorry a cafe with that id was not found in the database."
    }), 404
# HTTP DELETE - Delete Record
@app.route("/report-closed/<int:id>", methods=["DELETE"])
def delete(id):
    cafe = db.get_or_404(Cafe, id)
    key = request.args.get("api-key")
    api_key = "TopSecretAPIKey"
    if cafe and (api_key == key):
        db.session.delete(cafe)
        db.session.commit()
        return jsonify(success= {
            "success": "Successfully deleted the cafe."
        })
    elif cafe and (api_key != key):
        return jsonify(error = {
            "Not Found": "Sorry, that's not allowed, Make sure you have the correct api_key."
        }), 403

if __name__ == '__main__':
    app.run(debug=True)
