import os
from typing import List, Tuple

import psycopg2


DATABASE = os.environ.get('DATABASE_URL') or 'postgresql://web:web@localhost:5432/status_board'


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

    with psycopg2.connect(DATABASE) as sess:
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

    with psycopg2.connect(DATABASE) as sess:
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

    with psycopg2.connect(DATABASE) as sess:
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

    with psycopg2.connect(DATABASE) as sess:
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

    with psycopg2.connect(DATABASE) as sess:
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
    
    update
    set posted_ts = current_timestamp;
    """

    with psycopg2.connect(DATABASE) as sess:
        with sess.cursor() as cur:
            cur.execute(order, (dev_id,))
        sess.commit()


def post_gpu_info(dev_id: str, info: str):
    order = """
    insert into last_gpu_info(device_id, detail)
    values (%s, %s)
    
    on conflict on constraint last_gpu_info_un do
    
    update
    set detail = %s;
    """

    with psycopg2.connect(DATABASE) as sess:
        with sess.cursor() as cur:
            cur.execute(order, (dev_id, info, info))
        sess.commit()
