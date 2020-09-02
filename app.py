from datetime import datetime, timedelta
from pytz import timezone

from flask import Flask, render_template, request

from db import load_last_date, load_device_name, dev_name2dev_id, post_heartbeat

app = Flask(__name__)


@app.route('/', methods=["GET"])
def index():
    records = load_last_date()
    tz_jp = timezone('Asia/Tokyo')
    now = datetime.now(tz=tz_jp)
    past_times = []
    is_exceeded = []  # 一定期間，生存信号を送っていない場合 True
    for record in records:
        past_times.append(str(now - record[1].astimezone(tz_jp)).split('.')[0])
        is_exceeded.append(now > record[1].astimezone(tz_jp) + timedelta(days=1))

    # print(records)
    # print(past_times)
    # print(is_exceeded)
    return render_template('index.html',
                           records=records, past_times=past_times, is_exceeded=is_exceeded)


@app.route('/api/heartbeat', methods=["POST"])
def api_heartbeat():
    req_name = request.form['name']

    dev_names = load_device_name()
    if (req_name,) not in dev_names:
        return 'invalid name error\n'

    dev_id = dev_name2dev_id(req_name)

    try:
        post_heartbeat(dev_id)
    except Exception as e:
        return str(e)

    return 'successfully posted\n'


if __name__ == '__main__':
    app.run()
