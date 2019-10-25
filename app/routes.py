import base64
import os
from collections import defaultdict

from app import app, api, socketio
from flask import render_template
from flask import request, jsonify
from flask_restful import Resource
from flask_socketio import emit

from . import converter

root_url = "http://localhost:5000/"
load_id_dict = defaultdict(lambda: 0)
save_id_dict = defaultdict(lambda: 0)


@app.route("/")
@app.route("/index")
def index():
    return "HELLO WORLD!"


@app.route("/player/<int:id>")
def player(id):
    return render_template('player.html', id=id, root_url=root_url)


@app.route("/playground/<int:id1>")
def play_ground(id1):
    return render_template('play_ground.html', id1=id1, root_url=root_url)


@socketio.on("test", namespace="/test")
def test():
    print("test", "connected")
    emit('my response', {'data': 'Connected'})


@socketio.on('testing', namespace='/test')
def test_message(message):
    print(message)


@socketio.on('save image', namespace='/test')
def save_image(message):
    id, img = message['id'], message['img']

    dir = f"./app/resources/user/{id}/"
    if not os.path.exists(os.path.dirname(dir)):
        try:
            os.makedirs(os.path.dirname(dir))
        except:
            emit('save image response', {'status': False, 'msg': 'Fail to make a directory'}, broadcast=True)

    trimmed_img_base64 = img.replace('data:image/png;base64,', '')
    binary_img = base64.b64decode(trimmed_img_base64)

    file_path = f"{dir}/{save_id_dict[id]}.png"
    try:
        with open(file_path, "wb+") as fh:
            fh.write(binary_img)
        save_id_dict[id] += 1
        emit('save image response', {'status': True, 'msg': f'Successfully save file{file_path}'}, broadcast=True)
    except:
        emit('save image response', {'status': False, 'msg': f'Fail to save file{file_path}'}, broadcast=True)


@socketio.on('convert image', namespace='/test')
def convert_image(message):
    id = message['id']
    file_path = f'./app/resources/user/{id}/{load_id_dict[id]}.png'
    if not os.path.exists(file_path):
        emit('convert image response', {'status': False, 'msg': 'No image to process'}, broadcast=True)
        return

    try:
        possibility, idx = converter.convert(file_path)
        os.remove(file_path)
        emit('convert image response',
             {'status': True,
              'possibility': possibility,
              'label': idx,
              'msg': f'Successfully convert image {file_path}'},
             broadcast=True)

    except:
        emit('convert image response',
             {'status': False, 'msg': f'Fail to convert image {file_path}'},
             broadcast=True)
    load_id_dict[id] += 1