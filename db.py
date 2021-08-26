import os
from typing import List, Optional, Set, Tuple

import psycopg2


DATABASE = os.environ.get('DATABASE_URL') or 'postgresql://web:web@localhost:5432/status_board'


def select_device_last_heatbeat() -> List[Tuple]:
    """
    :return: list of (device_name, timestamp)
    """
    order = """
    SELECT device_name, last_heatbeat
      FROM devices
     ORDER BY device_name asc;
    """

    with psycopg2.connect(DATABASE) as sess:
        with sess.cursor() as cur:
            cur.execute(order)
            res = cur.fetchall()
    return res


def select_device_names() -> Set[str]:
    """
    :return: list of (device_name,)
    """
    order = """
    SELECT device_name
      FROM devices;
    """

    with psycopg2.connect(DATABASE) as sess:
        with sess.cursor() as cur:
            cur.execute(order)
            res: List[Tuple[str]] = cur.fetchall()
    return set(tp[0] for tp in res)


def select_return_message(dev_name: str) -> str:
    """
    :return: return_message of a device
    """
    order = """
    SELECT return_message
      FROM devices
     WHERE device_name = %s;
    """

    with psycopg2.connect(DATABASE) as sess:
        with sess.cursor() as cur:
            cur.execute(order, (dev_name,))
            res: Tuple[str] = cur.fetchone()
    return res[0]  # return single value


def select_device_last_detail() -> List[Tuple]:
    """
    :return: list of (device_name, last_detail)
    """
    order = """
    SELECT D.device_name, GM.last_detail
      FROM gpu_machines GM
     INNER JOIN devices D
        ON GM.machine_id = D.device_id
     ORDER BY D.device_name ASC;
    """

    with psycopg2.connect(DATABASE) as sess:
        with sess.cursor() as cur:
            cur.execute(order)
            res = cur.fetchall()
    return res


def post_heartbeat(dev_name: str):
    order = """
    UPDATE devices
       SET last_heartbeat = current_timestamp
     WHERE device_name = %s;
    """

    with psycopg2.connect(DATABASE) as sess:
        with sess.cursor() as cur:
            cur.execute(order, (dev_name,))
        sess.commit()


def post_gpu_info(dev_name: str, info: str):
    order = """
    UPDATE gpu_machines
       SET last_detail = %s
     WHERE machine_id = (
           SELECT device_id
             FROM devices
            WHERE device_name = %s AND has_gpu
    );
    """

    with psycopg2.connect(DATABASE) as sess:
        with sess.cursor() as cur:
            cur.execute(order, (info, dev_name))
        sess.commit()


def update_return_message(dev_name: str, return_message: str):
    order = """
    UPDATE devices
       SET return_message = %s
     WHERE device_name = %s;
    """

    with psycopg2.connect(DATABASE) as sess:
        with sess.cursor() as cur:
            cur.execute(order, (return_message, dev_name))
        sess.commit()


def register_device(dev_name: str, has_gpu: bool, return_message: Optional[str]):
    order_d = """
    INSERT INTO public.devices (device_name, has_gpu, return_message) VALUES
           (%s, %s, %s);
    """
    order_gm = """
    INSERT INTO public.gpu_machines (machine_id, last_detail) VALUES
           ((
           SELECT device_id
             FROM devices
            WHERE device_name = %s
           ),
           %s);
    """

    with psycopg2.connect(DATABASE) as sess:
        with sess.cursor() as cur:
            cur.execute(order_d, (dev_name, has_gpu, return_message))
            if has_gpu:
                cur.execute(order_gm, (dev_name, ''))
        sess.commit()
