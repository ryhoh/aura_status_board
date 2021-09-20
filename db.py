import datetime
import os
from typing import List, Optional, Set, Tuple

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_READ_COMMITTED
from pydantic import BaseModel


DATABASE = os.environ.get('DATABASE_URL') or 'postgresql://web:web@localhost:5432/status_board'


def gmt2jst(dt: datetime.datetime):
    return dt.astimezone(datetime.timezone(datetime.timedelta(hours=+9)))


class Device(BaseModel):
    device_name: str
    last_heartbeat_timestamp: datetime.datetime
    report: str
    return_message: str


def read_JWT_secret() -> str:
    """
    Read JWT secret

    :return: JWT secret
    """
    with psycopg2.connect(DATABASE) as conn:
        with conn.cursor() as cur:
            cur.execute("select secret from jwt;")
            res: List[str] = cur.fetchone()
            return res[0]


def read_password_from_users(name: str) -> bytes:
    """
    Read user's password

    :return: Hashed password if user exists.
    """

    SQL = """
    SELECT hashed_password
      FROM users
     WHERE user_name = %s;
    """

    with psycopg2.connect(DATABASE) as conn:
        with conn.cursor() as cur:
            cur.execute(SQL, (name,))
            res = cur.fetchone()
            if res is None:
                raise ValueError("User not exist:", name)
            return res[0].tobytes()


def select_devices() -> List[Device]:
    """
    :return: list of Device
    """
    SQL = """
    SELECT device_name, last_heartbeat, report, return_message
      FROM devices
     ORDER BY device_name asc;  -- this sort should be in javascript
    """

    with psycopg2.connect(DATABASE) as sess:
        sess.isolation_level = ISOLATION_LEVEL_READ_COMMITTED
        with sess.cursor() as cur:
            cur.execute(SQL)
            res: List[Tuple] = cur.fetchall()
    return [Device(**{
        'device_name': tp[0],
        'last_heartbeat_timestamp': gmt2jst(tp[1]),
        'report': tp[2],
        'return_message': tp[3],
    }) for tp in res]


def select_report(dev_name: str) -> str:
    """
    :return: report of a device
    """
    SQL = """
    SELECT report
      FROM devices
     WHERE device_name = %s;
    """

    with psycopg2.connect(DATABASE) as sess:
        sess.isolation_level = ISOLATION_LEVEL_READ_COMMITTED
        with sess.cursor() as cur:
            cur.execute(SQL, (dev_name,))
            res: Tuple[str] = cur.fetchone()
    return res[0]  # return single value


def select_return_message(dev_name: str) -> str:
    """
    :return: return_message of a device
    """
    SQL = """
    SELECT return_message
      FROM devices
     WHERE device_name = %s;
    """

    with psycopg2.connect(DATABASE) as sess:
        sess.isolation_level = ISOLATION_LEVEL_READ_COMMITTED
        with sess.cursor() as cur:
            cur.execute(SQL, (dev_name,))
            res: Tuple[str] = cur.fetchone()
    return res[0]  # return single value


def select_device_reports() -> List[Tuple]:
    """
    :return: list of (device_name, report)
    """
    SQL = """
    SELECT device_name, report
      FROM devices
     ORDER BY device_name ASC;
    """

    with psycopg2.connect(DATABASE) as sess:
        sess.isolation_level = ISOLATION_LEVEL_READ_COMMITTED
        with sess.cursor() as cur:
            cur.execute(SQL)
            res = cur.fetchall()
    return res


def post_heartbeat(dev_name: str, report: Optional[str]):
    SQL1 = """
    SELECT device_name
      FROM devices;
    """

    SQL2 = """
    UPDATE devices
       SET last_heartbeat = current_timestamp,
           report = %s
     WHERE device_name = %s;
    """

    with psycopg2.connect(DATABASE) as sess:
        sess.isolation_level = ISOLATION_LEVEL_READ_COMMITTED
        with sess.cursor() as cur:
            cur.execute(SQL1)
            valid_devices: Set[str] = set(tp[0] for tp in cur.fetchall())
            if dev_name not in valid_devices:
                raise ValueError('invalid device name')
            
            cur.execute(SQL2, (report if report is not None else '', dev_name))
        sess.commit()


def update_return_message(dev_name: str, return_message: str):
    SQL = """
    UPDATE devices
       SET return_message = %s
     WHERE device_name = %s;
    """

    with psycopg2.connect(DATABASE) as sess:
        sess.isolation_level = ISOLATION_LEVEL_READ_COMMITTED
        with sess.cursor() as cur:
            cur.execute(SQL, (return_message, dev_name))
        sess.commit()


def register_device(dev_name: str, report: Optional[str], return_message: Optional[str]):
    SQL1 = """
    INSERT INTO public.devices (device_name, report, return_message) VALUES
           (%s, %s, %s);
    """

    with psycopg2.connect(DATABASE) as sess:
        sess.isolation_level = ISOLATION_LEVEL_READ_COMMITTED
        with sess.cursor() as cur:
            cur.execute(SQL1, (
                dev_name,
                report if report is not None else '',
                return_message if return_message is not None else ''
            ))
        sess.commit()
