from typing import List
import datetime as dt
import random

import db


"""
Functions for MHPL (Machine-Hub Pipeline Language).

Pipeline:
    A process between devices.
    Pipeline receives parameters from device as parameter (which can be empty),
    processes it and return value to device (type).

Pipeline fuction must satisfy below:
    Receive str payloads.
    Return exactly one str object .

"""
def get_alive_device_n() -> str:
    devices: List[db.Device] = db.select_devices()
    return str(
        sum(
            dt.datetime.now(tz=dt.timezone(offset=dt.timedelta(hours=9)))
            - device.last_heartbeat_timestamp
            < dt.timedelta(hours=24)
            for device in devices
        )
    )


def get_device_n() -> str:
    return str(len(db.select_devices()))


def get_dead_device_n() -> str:
    return str(int(get_device_n()) - int(get_alive_device_n()))


def get_device_name_randomly() -> str:
    devices = db.select_devices()
    if len(devices) == 0:
        return ''
    return random.choice(devices).device_name


def get_report(device_name: str) -> str:
    return db.select_report(device_name)


def culc_plus(a: str, b: str) -> str:
    try:
        return str(int(a) + int(b))  # as int
    except ValueError:
        pass
    try:
        return str(float(a) + float(b))  # as float
    except ValueError:
        return a + b  # as str


def culc_minus(a: str, b: str) -> str:
    try:
        return str(int(a) - int(b))  # as int
    except ValueError:
        pass
    try:
        return str(float(a) - float(b))  # as float
    except ValueError:
        return 'NaN'


def culc_times(a: str, b: str) -> str:
    try:
        return str(int(a) * int(b))  # as int
    except ValueError:
        pass
    try:
        return str(float(a) * float(b))  # as float
    except ValueError:
        if isinstance(b, int):
            return a * int(b)  # 'foo' * 3 = 'foofoofoo'
        return 'NaN'


def culc_divide(a: str, b: str) -> str:
    try:
        if a % b == 0:  # as int
            return str(int(a) // int(b))
        return str(int(a) / int(b))
    except ValueError:
        pass
    try:
        return str(float(a) / float(b))  # as float
    except ValueError:
        return 'NaN'
    