from flask import Flask
from flask_restful import Api, Resource, reqparse, abort, fields, marshal_with
from flask_sqlalchemy import SQLAlchemy
from base64 import b64encode

app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
db = SQLAlchemy(app)

BASE = "https://api-rest-t2.herokuapp.com/"


class ArtistModel(db.Model):
    id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    albums = db.Column(db.String)
    tracks = db.Column(db.String)
    self_a = db.Column(db.String)


class AlbumModel(db.Model):
    id = db.Column(db.String, primary_key=True)
    artist_id = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=False)
    genre = db.Column(db.String, nullable=False)
    artist = db.Column(db.String)
    tracks = db.Column(db.String)
    self_a = db.Column(db.String)


class TrackModel(db.Model):
    id = db.Column(db.String, primary_key=True)
    album_id = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=False)
    duration = db.Column(db.Float, nullable=False)
    times_played = db.Column(db.Integer, default=0)
    artist = db.Column(db.String)
    album = db.Column(db.String)
    self_a = db.Column(db.String)

db.create_all()

artists_post_args = reqparse.RequestParser()
artists_post_args.add_argument("name", type=str, help="Falta el nombre del artista", required=True)
artists_post_args.add_argument("age", type=int, help="Falta la edad del artista", required=True)

albums_post_args = reqparse.RequestParser()
albums_post_args.add_argument("name", type=str, help="Falta el nombre del album", required=True)
albums_post_args.add_argument("genre", type=str, help="Falta el genero del album", required=True)

tracks_post_args = reqparse.RequestParser()
tracks_post_args.add_argument("name", type=str, help="Falta el nombre de la canción", required=True)
tracks_post_args.add_argument("duration", type=float, help="Falta la duracion de la canción", required=True)

'''
def abort_if_artist_doesnt_exist(artist_id):
    if artist_id not in artists:
        abort(404, message="El artista no existe")
'''

resource_fields_artists = {
    'id': fields.String,
    'name': fields.String,
    'age': fields.Integer,
    'albums': fields.String,
    'tracks': fields.String,
    'self_a': fields.String
}

resource_fields_albums = {
    'id': fields.String,
    'artist_id': fields.String,
    'name': fields.String,
    'genre': fields.String,
    'artist': fields.String,
    'tracks': fields.String,
    'self_a': fields.String
}

resource_fields_track = {
    'id': fields.String,
    'album_id': fields.String,
    'name': fields.String,
    'duration': fields.Float,
    'times_played': fields.Integer,
    'artist': fields.String,
    'album': fields.String,
    'self_a': fields.String
}


class Artist(Resource):
    @marshal_with(resource_fields_artists)
    def get(self, artist_id):
        result = ArtistModel.query.filter_by(id=artist_id).first()
        if not result:
            abort(404, message="No existe un Artista con ese ID")
        return result, 200

    def delete(self, artist_id):
        result = ArtistModel.query.filter_by(id=artist_id).first()
        if not result:
            abort(404, message="No existe un Artista con ese ID")
        result1 = AlbumModel.query.filter_by(artist_id=artist_id).all()
        for a in result1:
            db.session.delete(a)
        result2 = TrackModel.query.filter_by(artist=f"artists/{artist_id}").all()
        for t in result2:
            db.session.delete(t)
        db.session.delete(result)
        db.session.commit()
        return '', 204


class Artists(Resource):
    @marshal_with(resource_fields_artists)
    def get(self):
        result = ArtistModel.query.all()
        if not result:
            abort(404, message="No hay artistas en la base de datos")
        return result, 200

    @marshal_with(resource_fields_artists)
    def post(self):
        args = artists_post_args.parse_args()
        artist_name = args['name']
        encoded = b64encode(artist_name.encode()).decode('utf-8')
        print(f"El id antes de truncar es {encoded}")
        encoded = encoded[:22]
        print(f"El id resultante es {encoded}")
        result = ArtistModel.query.filter_by(id=encoded).first()
        if result:
            return result, 409
        artist_albums = BASE + f"artists/{encoded}/albums"
        artist_tracks = BASE + f"artists/{encoded}/tracks"
        self_artist = BASE + f"artists/{encoded}"
        artist = ArtistModel(id=encoded, name=artist_name, age=args['age'], albums=artist_albums, tracks=artist_tracks,
                             self_a=self_artist)
        db.session.add(artist)
        db.session.commit()
        return artist, 201


class ArtistAlbums(Resource):
    @marshal_with(resource_fields_albums)
    def get(self, artist_id):
        result1 = ArtistModel.query.filter_by(id=artist_id).first()
        if not result1:
            abort(404, message="No existe un Artista con ese ID")
        result = AlbumModel.query.filter_by(artist_id=artist_id).all()
        return result, 200

    @marshal_with(resource_fields_albums)
    def post(self, artist_id):
        result1 = ArtistModel.query.filter_by(id=artist_id).first()
        if not result1:
            abort(422, message="No existe un Artista con ese ID")
        args = albums_post_args.parse_args()
        pre_codificado = args['name'] + ":" + artist_id
        encoded = b64encode(pre_codificado.encode()).decode('utf-8')[:22]
        result2 = AlbumModel.query.filter_by(id=encoded).first()
        if result2:
            return result2, 409
        album_artist = BASE + f"artists/{artist_id}"
        album_tracks = BASE + f"albums/{encoded}/tracks"
        self_album = BASE + f"albums/{encoded}"
        album = AlbumModel(id=encoded, artist_id=artist_id, name=args['name'], genre=args['genre'],
                           artist=album_artist, tracks=album_tracks, self_a=self_album)
        db.session.add(album)
        db.session.commit()
        return album, 201


class ArtistAlbumsPlay(Resource):

    @marshal_with(resource_fields_track)
    def put(self, artist_id):
        result = ArtistModel.query.filter_by(id=artist_id).first()
        if not result:
            abort(404, message="No existe un Artista con ese ID")
        artist = BASE + f"artists/{artist_id}"
        result1 = TrackModel.query.filter_by(artist=artist).all()
        for t in result1:
            t.times_played += 1
            db.session.commit()
        return 'Se reproducieron todas las canciones del artista', 200


class ArtistTracks(Resource):
    @marshal_with(resource_fields_track)
    def get(self, artist_id):
        result1 = ArtistModel.query.filter_by(id=artist_id).first()
        if not result1:
            abort(404, message="No existe un Artista con ese ID")
        artist = BASE + f"artists/{artist_id}"
        result = TrackModel.query.filter_by(artist=artist).all()
        return result, 200


class Albums(Resource):
    @marshal_with(resource_fields_albums)
    def get(self):
        result = AlbumModel.query.all()
        return result, 200


class Album(Resource):
    @marshal_with(resource_fields_albums)
    def get(self, album_id):
        result = AlbumModel.query.filter_by(id=album_id).first()
        if not result:
            abort(404, message="No existe un album con ese ID")
        return result, 200

    def delete(self, album_id):
        result = AlbumModel.query.filter_by(id=album_id).first()
        if not result:
            abort(404, message="No existe un album con ese ID")
        result2 = TrackModel.query.filter_by(album_id=album_id).all()
        for t in result2:
            db.session.delete(t)
        db.session.delete(result)
        db.session.commit()
        return '', 204


class AlbumTracks(Resource):
    @marshal_with(resource_fields_track)
    def get(self, album_id):
        result1 = AlbumModel.query.filter_by(id=album_id).first()
        if not result1:
            abort(404, message="No existe un album con ese ID")
        result = TrackModel.query.filter_by(album_id=album_id).all()
        return result, 200

    @marshal_with(resource_fields_track)
    def post(self, album_id):
        result1 = AlbumModel.query.filter_by(id=album_id).first()
        if not result1:
            abort(422, message="No existe un album con ese ID")
        args = tracks_post_args.parse_args()
        pre_codificado = args['name'] + ":" + album_id
        encoded = b64encode(pre_codificado.encode()).decode('utf-8')[:22]
        result2 = AlbumModel.query.filter_by(id=encoded).first()
        if result2:
            return result2, 409
        track_artist = BASE + f"artists/{result1.artist_id}"
        track_album = BASE + f"albums/{album_id}"
        self_track = BASE + f"tracks/{encoded}"
        track = TrackModel(id=encoded, album_id=album_id, name=args['name'], duration=args['duration'],
                           times_played=0, artist=track_artist, album=track_album, self_a=self_track)
        db.session.add(track)
        db.session.commit()
        return track, 201


class AlbumTracksPlay(Resource):

    @marshal_with(resource_fields_track)
    def put(self, album_id):
        result1 = AlbumModel.query.filter_by(id=album_id).first()
        if not result1:
            abort(404, message="No existe un album con ese ID")
        result = TrackModel.query.filter_by(album_id=album_id).all()
        for t in result:
            t.times_played += 1
            db.session.commit()
        return 'Se reproducieron todas las canciones del album', 200


class Tracks(Resource):
    @marshal_with(resource_fields_track)
    def get(self):
        result = TrackModel.query.all()
        return result, 200


class Track(Resource):
    @marshal_with(resource_fields_track)
    def get(self, track_id):
        result = TrackModel.query.filter_by(id=track_id).first()
        if not result:
            abort(404, message="No existe una canción con ese ID")
        return result, 200

    def delete(self, track_id):
        result = TrackModel.query.filter_by(id=track_id).first()
        if not result:
            abort(404, message="No existe una canción con ese ID")
        db.session.delete(result)
        db.session.commit()
        return '', 204


class TrackPlay(Resource):

    @marshal_with(resource_fields_track)
    def put(self, track_id):
        result = TrackModel.query.filter_by(id=track_id).first()
        if not result:
            abort(404, message="No existe una canción con ese ID")
        result.times_played += 1
        db.session.commit()
        return 'se reprodujo la cancion', 200


api.add_resource(Artists, "/artists")
api.add_resource(Artist, "/artists/<string:artist_id>")
api.add_resource(ArtistAlbums, "/artists/<string:artist_id>/albums")
api.add_resource(ArtistAlbumsPlay, "/artists/<string:artist_id>/albums/play")
api.add_resource(ArtistTracks, "/artists/<string:artist_id>/tracks")
api.add_resource(Albums, "/albums")
api.add_resource(Album, "/albums/<string:album_id>")
api.add_resource(AlbumTracks, "/albums/<string:album_id>/tracks")
api.add_resource(AlbumTracksPlay, "/albums/<string:album_id>/tracks/play")
api.add_resource(Tracks, "/tracks")
api.add_resource(Track, "/tracks/<string:track_id>")
api.add_resource(TrackPlay, "/tracks/<string:track_id>/play")

if __name__ == "__main__":  # Este __main__ es el nombre del archibo? o da lo mismo el nombre que le ponga al archivo?
    app.run(debug=True)
