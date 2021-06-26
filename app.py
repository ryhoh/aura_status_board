import datetime
from typing import Optional

from fastapi import FastAPI, Form
from fastapi.encoders import jsonable_encoder
from fastapi.responses import FileResponse, JSONResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from passlib.context import CryptContext
import uvicorn

import db


hashed_pw = b'$2b$12$3jMfq3IMzFOzJ.LqXiaelOBKbU4A7n.LyBKNAR39lTyKF44WcPscK'
pw_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")


def gmt2jst(dt: datetime.datetime):
    return dt.astimezone(datetime.timezone(datetime.timedelta(hours=+9)))


def verify_password(plain_password: str, hashed_password: bytes):
    return pw_context.verify(plain_password, hashed_password)


@app.get('/')
async def root():
    return FileResponse('static/index.html')


@app.get('/json/last_signal_ts')
def json_last_signal_ts():
    orig_records = db.select_last_date_heartbeat()
    records = [{'name': record[0], 'timestamp': str(gmt2jst(record[1]))} for record in orig_records]
    return JSONResponse(jsonable_encoder(records))


@app.get('/json/last_gpu_info')
def json_last_gpu_info():
    orig_gpu_info = db.select_device_with_gpuinfo()  # [(id, name, smi_text) ... ]
    gpu_info = [{'name': record[1], 'detail': record[2]} for record in orig_gpu_info]
    return JSONResponse(jsonable_encoder(gpu_info))


@app.post('/api/heartbeat')
def api_heartbeat(password: str = Form(...), name: str = Form(...), nvidia_smi: Optional[str] = Form(None)):
    if not verify_password(password, hashed_pw):  # check credential
        return PlainTextResponse(content='invalid password\n', status_code=403)

    try:  # getting device id (register new record if not exist)
        dev_id = db.device_name_to_device_id(name)
    except ValueError:
        dev_id = db.register_device(name)

    if nvidia_smi is not None:
        db.post_gpu_info(dev_id, nvidia_smi)

    try:  # post timestamp
        db.post_heartbeat(dev_id)
    except Exception as e:
        return PlainTextResponse(content=str(e), status_code=500)

    return PlainTextResponse(content='successfully posted\n', status_code=200)


if __name__ == '__main__':
    uvicorn.run('app:app', host='0.0.0.0', port=8000)
