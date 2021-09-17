from datetime import timedelta
from typing import List, Optional, Union

from fastapi import Depends, FastAPI, Form, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import FileResponse, JSONResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordRequestForm
from passlib.context import CryptContext
import uvicorn

import db
from db import Device
import user_authorization as user_auth


hashed_api_password = b'$2b$12$3jMfq3IMzFOzJ.LqXiaelOBKbU4A7n.LyBKNAR39lTyKF44WcPscK'
pw_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get('/')
async def root():
    return FileResponse('static/index.html')


@app.get('/json/signals')
def json_last_signal_ts():
    devices: List[Device] = db.select_devices()
    return JSONResponse(jsonable_encoder([device.dict() for device in devices]))


@app.get('/json/last_gpu_info')
def json_last_gpu_info():
    orig_gpu_info = db.select_device_last_detail()  # [(name, smi_text) ... ]
    gpu_info = [{'name': record[0], 'detail': record[1]} for record in orig_gpu_info]
    return JSONResponse(jsonable_encoder(gpu_info))


@app.post('/api/heartbeat')
def api_heartbeat(
    password: str = Form(...),
    name: str = Form(...),
    nvidia_smi: Optional[str] = Form(None)
):
    if not pw_context.verify(password, hashed_api_password):  # check credential
        return PlainTextResponse(content='invalid password\n', status_code=403)

    try:
        db.post_heartbeat(name, nvidia_smi)
    except ValueError:
        return PlainTextResponse(content='invalid name\n', status_code=400)

    return PlainTextResponse(
        content=db.select_return_message(name) or 'successfully posted\n',
        status_code=200
    )

@app.post('/api/return_message')
def api_register_return_message(
    password: str = Form(...),
    name: str = Form(...),
    return_message: str = Form(...)
):
    if not pw_context.verify(password, hashed_api_password):  # check credential
        return PlainTextResponse(content='invalid password\n', status_code=403)

    db.update_return_message(name, return_message)
    return PlainTextResponse('successfully registered\n', status_code=200)


@app.post('/api/register/device')
def api_register_device(
    password: str = Form(...),
    name: str = Form(...),
    has_gpu: Optional[str] = Form(None),
    return_message: Optional[str] = Form(None)
):
    if not pw_context.verify(password, hashed_api_password):  # check credential
        return PlainTextResponse(content='invalid password\n', status_code=403)

    db.register_device(name, (has_gpu is not None), return_message)
    return PlainTextResponse('successfully registered\n', status_code=200)


@app.post('/api/token')
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user: Union[user_auth.UserInDB, bool] = user_auth.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=user_auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = user_auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


if __name__ == '__main__':
    uvicorn.run('app:app', host='127.0.0.1', port=8000)
