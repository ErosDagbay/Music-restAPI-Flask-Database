from flask import Flask
from flask_restful import Api, Resource, reqparse
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
api = Api(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///songs.db"
db = SQLAlchemy(app)

class Song(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    artist = db.Column(db.String(100))

    def to_json(self):
        return {"id": self.id, "title": self.title, "artist": self.artist}

parser = reqparse.RequestParser()
parser.add_argument("title", required=True)
parser.add_argument("artist", required=True)

update_parser = reqparse.RequestParser()
update_parser.add_argument("title")
update_parser.add_argument("artist")

class Songs(Resource):
    def get(self):
        songs = Song.query.all()
        return {"songs": [s.to_json() for s in songs]}

    def post(self):
        data = parser.parse_args()
        song = Song(title=data["title"], artist=data["artist"])
        db.session.add(song)
        db.session.commit()
        return song.to_json(), 201


class SongByID(Resource):
    def patch(self, id):
        song = Song.query.get_or_404(id)
        data = update_parser.parse_args()

        if data["title"]:
            song.title = data["title"]
        if data["artist"]:
            song.artist = data["artist"]

        db.session.commit()
        return song.to_json()

    def delete(self, id):
        song = Song.query.get_or_404(id)
        db.session.delete(song)
        db.session.commit()
        return {"message": "deleted"}

# route registration
api.add_resource(Songs, "/songs")
api.add_resource(SongByID, "/songs/<int:id>")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
    