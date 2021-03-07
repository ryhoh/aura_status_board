import os
from typing import Dict, List, Tuple

import psycopg2


DB = os.environ.get('DATABASE_URL')


def _connect():
    if DB is None:  # for debugging
        return psycopg2.connect(host="localhost", user="web", password="web", database="status_board")
    else:
        return psycopg2.connect(DB)


def select_last_date_heartbeat() -> List[Tuple]:
    """
    :return: list of (device_name, timestamp)
    """
    order = """
    select dev.name as name, hb.posted_ts as last_ts
    from latest_heartbeat as hb
    join devices as dev
    on hb.device_id = dev.id
    order by name asc;
    """

    with _connect() as sess:
        with sess.cursor() as cur:
            cur.execute(order)
            res = cur.fetchall()

    return res


def select_device_names() -> List[Tuple]:
    """
    :return: list of (device_name,)
    """
    order = """
    select name
    from devices;
    """

    with _connect() as sess:
        with sess.cursor() as cur:
            cur.execute(order)
            res = cur.fetchall()

    return res


def select_device_with_gpuinfo() -> List[Tuple]:
    order = """
    select d.id, d.name, lgi.detail 
    from devices d
    join last_gpu_info lgi
    on d.id = lgi.device_id
    order by d.id asc;
    """

    with _connect() as sess:
        with sess.cursor() as cur:
            cur.execute(order)
            res = cur.fetchall()

    return res


def device_name_to_device_id(dev_name: str) -> str:
    """
    :param str dev_name: device name
    :return: device_id corresponding to the device name
    :raises: ValueError when the device name does not exist
    """
    order = """
    select id
    from devices
    where name = %s;
    """

    with _connect() as sess:
        with sess.cursor() as cur:
            cur.execute(order, (dev_name,))
            res = cur.fetchall()

    try:
        return res[0][0]  # single value
    except IndexError:
        raise ValueError("unregistered dev_name")


def register_device(dev_name: str) -> str:
    """
    Register a device
    :param str dev_name: device name
    :return: device_id corresponding to the device name
    """
    order = """
    insert into devices(name)
    values (%s)
    returning id;
    """

    with _connect() as sess:
        with sess.cursor() as cur:
            cur.execute(order, (dev_name,))
            res = cur.fetchall()
        sess.commit()

    return res[0][0]  # single value


def post_heartbeat(dev_id: str):
    order = """
    insert into latest_heartbeat(device_id, posted_ts)
    values (%s, current_timestamp)
    
    on conflict on constraint latest_heartbeat_un do
    
    update latest_heartbeat
    set posted_ts = current_timestamp
    where device_id = %s;
    """

    with _connect() as sess:
        with sess.cursor() as cur:
            cur.execute(order, (dev_id, dev_id))
        sess.commit()


def post_gpu_info(dev_id: str, info: str):
    order = """
    update last_gpu_info
    set detail = %s
    where device_id = %s;
    """

    with _connect() as sess:
        with sess.cursor() as cur:
            cur.execute(order, (info, dev_id))
        sess.commit()
