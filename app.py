from datetime import datetime, timedelta, timezone

from flask import Flask, render_template, request, Response
from flask_bcrypt import Bcrypt

import db


hashed_pw = b'$2b$12$3jMfq3IMzFOzJ.LqXiaelOBKbU4A7n.LyBKNAR39lTyKF44WcPscK'

app = Flask(__name__)
bcrypt = Bcrypt(app)


@app.route('/', methods=["GET"])
def index():
    records = db.select_last_date_heartbeat()
    tz_jp = timezone(timedelta(hours=+9), 'JST')
    now = datetime.now(tz=tz_jp)
    past_times = []
    is_exceeded = []  # 一定期間，生存信号を送っていない場合 True
    for record in records:
        past_times.append(str(now - record[1].astimezone(tz_jp)).split('.')[0])
        is_exceeded.append(now > record[1].astimezone(tz_jp) + timedelta(days=1))

    dev_with_gpu = db.select_device_with_gpuinfo()  # [(id, name, smi_text) ... ]

    return render_template('index.html',
                           dev_with_gpu=dev_with_gpu,
                           records=records, past_times=past_times, is_exceeded=is_exceeded)


@app.route('/api/heartbeat', methods=["POST"])
def api_heartbeat():
    req_name = request.form['name']
    pw = request.form['password']
    if not bcrypt.check_password_hash(hashed_pw, pw):
        return Response(response='invalid password\n', status=403)

    try:
        dev_id = db.dev_name2dev_id(req_name)
    except ValueError:
        return Response(response='unregistered name\n', status=400)

    if 'nvidia_smi' in request.form.keys():
        info = request.form['nvidia_smi'].replace(" ", "&nbsp;")
        db.post_gpu_info(dev_id, info)

    # dev_names = db.select_device_names()
    # if (req_name,) not in dev_names:
    #     return Response(response='unregistered name\n', status=400)

    try:
        db.post_heartbeat(dev_id)
    except Exception as e:
        return Response(response=str(e), status=500)

    return Response(response='successfully posted\n', status=200)


if __name__ == '__main__':
    app.run()
