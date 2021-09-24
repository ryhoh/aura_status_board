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
from pipeline import FunctionNotFoundError, FunctionParamUnmatchError, Pipeline
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
    devices = [device.dict() for device in devices]
    for device in devices:
        device['last_heartbeat_timestamp'] = str(device['last_heartbeat_timestamp'])
    return JSONResponse(jsonable_encoder(devices))


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
    
    return_message = db.select_return_message(name)
    try:
        content = Pipeline.feed(return_message)
    except (FunctionNotFoundError, FunctionParamUnmatchError):
        content = return_message

    return PlainTextResponse(
        content=content,
        status_code=200
    )

@app.post('/api/v2/heartbeat')
def api_heartbeat(
    password: str = Form(...),
    device_name: str = Form(...),
    report: Optional[str] = Form(None)
):
    if not pw_context.verify(password, hashed_api_password):  # check credential
        return PlainTextResponse(content='invalid password\n', status_code=403)

    try:
        db.post_heartbeat(device_name, report)
    except ValueError:
        return PlainTextResponse(content='invalid name\n', status_code=400)
    
    return_message = db.select_return_message(device_name)
    try:
        content = Pipeline.feed(return_message)
    except (FunctionNotFoundError, FunctionParamUnmatchError):
        content = return_message

    return PlainTextResponse(
        content=content,
        status_code=200
    )

@app.post('/api/return_message')
def api_register_return_message(
    user: user_auth.UserInDB = Depends(user_auth.get_current_user),
    name: str = Form(...),
    return_message: str = Form(...)
):
    if not user:  # User authorization
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Process Special str
    if return_message == '#empty':
        return_message = ''

    db.update_return_message(name, return_message)
    return PlainTextResponse('successfully registered\n', status_code=200)


@app.post('/api/v2/register/device')
def api_register_device(
    user: user_auth.UserInDB = Depends(user_auth.get_current_user),
    device_name: str = Form(...),
):
    if not user:  # User authorization
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if len(device_name) < 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Device name must be more than 3 characters.",
        )

    try:
        db.register_device(device_name, None, None)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This device is already registered.",
        )
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
