import os
from typing import Dict, List, Tuple

import psycopg2


DB = os.environ.get('DATABASE_URL')


def _connect():
    if DB is None:  # for debugging
        return psycopg2.connect(host="localhost", user="web", password="web", database="status_board")
    else:
        return psycopg2.connect(DB)


def load_last_date() -> List[Tuple]:
    order = """
    select dev.name as name, max(hb.posted_ts) as last_ts
    from heartbeat_log as hb
    join devices as dev
    on hb.device_id = dev.id
    group by dev.id;
    """

    with _connect() as sess:
        with sess.cursor() as cur:
            cur.execute(order)
            res = cur.fetchall()

    return res


def load_device_name() -> List[Tuple]:
    order = """
    select distinct name
    from devices;
    """

    with _connect() as sess:
        with sess.cursor() as cur:
            cur.execute(order)
            res = cur.fetchall()

    return res


def dev_name2dev_id(dev_name: str) -> str:
    order = """
    select id
    from devices
    where name = %s;
    """

    with _connect() as sess:
        with sess.cursor() as cur:
            cur.execute(order, (dev_name,))
            res = cur.fetchall()

    return res[0][0]  # single value


def post_heartbeat(dev_id: str):
    order = """
    insert into heartbeat_log (device_id) values (%s);
    """

    with _connect() as sess:
        with sess.cursor() as cur:
            cur.execute(order, (dev_id,))
        sess.commit()
