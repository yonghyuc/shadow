from app import app, api
from flask import render_template
from flask_restful import Resource
from flask import request, jsonify

import base64
from collections import defaultdict
import os
from . import converter


root_url = "http://localhost:5000/"
load_id_dict = defaultdict(lambda: -1)
save_id_dict = defaultdict(lambda: -1)


@app.route("/")
@app.route("/index")
def index():
    return "HELLO WORLD!"


@app.route("/player/<int:id>")
def player_1(id):
    return render_template('player.html', id=id, root_url=root_url)


class Image(Resource):
    def get(self, id):
        file_name = load_id_dict[id]
        if file_name < 0 or file_name > save_id_dict[id]:
            return 'No image to process'
        load_id_dict[id] += 1
        possibility, idx = converter.convert(f'./app/resources/user/{id}/{file_name}.png')
        return jsonify(possibility=possibility, idx=idx)

    def post(self, id):
        image_data = request.data

        if not os.path.exists(os.path.dirname(f"./app/resources/user/{id}/")):
            try:
                os.makedirs(os.path.dirname(f"./app/resources/user/{id}/"))
            except OSError as exc: # Guard against race condition
                return 'Fail to make a directory'

        trimmed_img_base64 = image_data.decode("utf-8").replace('data:image/png;base64,', '')
        binary_img = base64.b64decode(trimmed_img_base64)

        save_id_dict[id] += 1
        with open(f"./app/resources/user/{id}/{save_id_dict[id]}.png", "wb+") as fh:
            fh.write(binary_img)

        return f'this is the POST {id}'

    def delete(self, id):
        pass

api.add_resource(Image, '/player/image/<int:id>')
