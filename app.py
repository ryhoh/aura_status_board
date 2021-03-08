from datetime import datetime, timedelta, timezone
import json

from flask import Flask, request, Response
from flask_bcrypt import Bcrypt

import db


hashed_pw = b'$2b$12$3jMfq3IMzFOzJ.LqXiaelOBKbU4A7n.LyBKNAR39lTyKF44WcPscK'

app = Flask(__name__)
bcrypt = Bcrypt(app)


def gmt2jst(dt: datetime):
    return dt.astimezone(timezone(timedelta(hours=+9)))


@app.route('/', methods=["GET"])
def index():
    return app.send_static_file('index.html')


@app.route('/json/last_signal_ts', methods=["GET"])
def json_last_signal_ts():
    orig_records = db.select_last_date_heartbeat()
    records = [{'name': record[0], 'timestamp': str(gmt2jst(record[1]))} for record in orig_records]
    records = json.dumps(records)
    return Response(response=records, status=200)


@app.route('/json/last_gpu_info', methods=["GET"])
def json_last_gpu_info():
    orig_gpu_info = db.select_device_with_gpuinfo()  # [(id, name, smi_text) ... ]
    gpu_info = [{'name': record[1], 'detail': record[2]} for record in orig_gpu_info]
    gpu_info = json.dumps(gpu_info)
    return Response(response=gpu_info, status=200)


@app.route('/api/heartbeat', methods=["POST"])
def api_heartbeat():
    try:  # check credential
        pw = request.form['password']
    except KeyError:
        return Response(response='password cannot be empty\n', status=400)
    if not bcrypt.check_password_hash(hashed_pw, pw):
        return Response(response='invalid password\n', status=403)

    try:  # check device name
        req_name = request.form['name']
    except KeyError:  # empty
        return Response(response='name cannot be empty\n', status=400)

    try:  # getting device id (register new record if not exist)
        dev_id = db.device_name_to_device_id(req_name)
    except ValueError:
        dev_id = db.register_device(req_name)

    if 'nvidia_smi' in request.form.keys():  # update gpu-info if device has nvidia_smi
        info = request.form['nvidia_smi']
        db.post_gpu_info(dev_id, info)

    try:  # post timestamp
        db.post_heartbeat(dev_id)
    except Exception as e:
        return Response(response=str(e), status=500)

    return Response(response='successfully posted\n', status=200)


if __name__ == '__main__':
    app.run()
