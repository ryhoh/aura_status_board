--------------------
-- Table Definition
--------------------

CREATE TABLE public.devices (
       device_id SERIAL NOT NULL,
       device_name VARCHAR(32) NOT NULL,
       last_heartbeat TIMESTAMP(0) NULL,
       report VARCHAR(4096) DEFAULT '' NOT NULL,
       return_message VARCHAR(4096) DEFAULT '' NOT NULL,
       is_active BOOLEAN DEFAULT TRUE NOT NULL,
       CONSTRAINT devices_pk PRIMARY KEY (device_id),
       CONSTRAINT devices_un UNIQUE (device_name)
);

CREATE TABLE public.jwt (
       secret CHAR(64) NOT NULL
);

CREATE TABLE public.users (
       user_name VARCHAR(16) NOT NULL,
       hashed_password BYTEA NOT NULL,
       CONSTRAINT users_pk PRIMARY KEY (user_name)
);

CREATE TABLE public.heartbeat_log (
       device_id int4 NOT NULL,
       heartbeat_ts TIMESTAMP(0) NOT NULL,
       CONSTRAINT heartbeat_log_pk PRIMARY KEY (device_id, heartbeat_ts),
       CONSTRAINT heartbeat_log_fk_device_id FOREIGN KEY (device_id) REFERENCES public.devices(device_id) ON DELETE CASCADE ON UPDATE CASCADE
);


--------------------
-- Data Insertion
--------------------

INSERT INTO public.devices (device_name,last_heartbeat,report,return_message) VALUES
       ('GPU480',current_timestamp,'GPU Information Here.',''),
       ('SMC101',current_timestamp,'','Hello SMC!'),
       ('AGP092',current_timestamp,'Mon Mar  8 21:37:43 2021
 -----------------------------------------------------------------------------
| NVIDIA-SMI 450.102.04   Driver Version: 450.102.04   CUDA Version: 11.0     |
|------------------------------- ---------------------- ---------------------- ','Loooooooooooooong message!'),
       ('AGP093','2021-03-12 23:30:25','','');

INSERT INTO public.heartbeat_log (device_id, heartbeat_ts) VALUES
       (1, current_timestamp),
       (1, current_timestamp - interval '23 hour'),
       (1, current_timestamp - interval '22 hour'),
       (1, current_timestamp - interval '21 hour'),
       (1, current_timestamp - interval '20 hour'),
       (1, current_timestamp - interval '19 hour'),
       (1, current_timestamp - interval '18 hour'),
       (1, current_timestamp - interval '17 hour'),
       (1, current_timestamp - interval '16 hour'),
       (1, current_timestamp - interval '15 hour'),
       (1, current_timestamp - interval '14 hour'),
       (1, current_timestamp - interval '13 hour'),
       (1, current_timestamp - interval '12 hour'),
       (1, current_timestamp - interval '11 hour'),
       (1, current_timestamp - interval '10 hour'),
       (1, current_timestamp - interval '9 hour'),
       (1, current_timestamp - interval '8 hour'),
       (1, current_timestamp - interval '7 hour'),
       (1, current_timestamp - interval '6 hour'),
       (1, current_timestamp - interval '5 hour'),
       (1, current_timestamp - interval '4 hour'),
       (1, current_timestamp - interval '3 hour'),
       (1, current_timestamp - interval '2 hour'),
       (1, current_timestamp - interval '1 hour'),
       (2, current_timestamp),
       (2, current_timestamp - interval '1 hour'),
       (3, current_timestamp),
       (4, '2021-03-12 23:30:00');

INSERT INTO public.jwt VALUES
       ('cc125635c56e2b29e842b7c520a5304eda31c3f0d409c09a911bcc5e742dcd60');

INSERT INTO public.users VALUES
       ('ryhoh', '$2b$12$uWqI2KUFmu9j.FBetR0HGOiXYLeeTNWrlBq0skxYi2iHChhm35vT.');
