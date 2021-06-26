--------------------
-- Sequence Definition
--------------------

CREATE SEQUENCE latest_heartbeat_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    START WITH 1
    NO CYCLE;


--------------------
-- Table Definition
--------------------

-- DROP TABLE public.devices;
CREATE TABLE public.devices (
	id serial NOT NULL,
	"name" varchar(256) NOT NULL,
	has_gpu bool NOT NULL,
	CONSTRAINT devices_pk PRIMARY KEY (id),
	CONSTRAINT devices_un UNIQUE (name)
);

-- DROP TABLE public.last_gpu_info;
CREATE TABLE public.last_gpu_info (
	device_id int4 NOT NULL,
	detail varchar(4096) NOT NULL,
	CONSTRAINT last_gpu_info_pk PRIMARY KEY (device_id),
	CONSTRAINT last_gpu_info_un UNIQUE (device_id),
	CONSTRAINT last_gpu_info_fk FOREIGN KEY (device_id) REFERENCES public.devices(id) ON DELETE RESTRICT ON UPDATE RESTRICT
);

-- DROP TABLE public.latest_heartbeat;
CREATE TABLE public.latest_heartbeat (
	posted_ts timestamp(0) NULL,
	device_id int4 NOT NULL DEFAULT nextval('latest_heartbeat_id_seq'::regclass),
	CONSTRAINT latest_heartbeat_pk PRIMARY KEY (device_id),
	CONSTRAINT latest_heartbeat_un UNIQUE (device_id),
	CONSTRAINT latest_heartbeat_fk FOREIGN KEY (device_id) REFERENCES public.devices(id) ON DELETE RESTRICT ON UPDATE RESTRICT
);


--------------------
-- Data Insertion
--------------------

INSERT INTO public.devices ("name",has_gpu) VALUES
	 ('takenaka_dl',true),
	 ('SMC101',false),
	 ('AGP092',true),
	 ('AGP093',true);

INSERT INTO public.last_gpu_info (device_id,detail) VALUES
	 (1,'testtesttest'),
	 (3,'Mon Mar  8 21:37:43 2021
 -----------------------------------------------------------------------------
| NVIDIA-SMI 450.102.04   Driver Version: 450.102.04   CUDA Version: 11.0     |
|------------------------------- ---------------------- ---------------------- ');

INSERT INTO public.latest_heartbeat (posted_ts) VALUES
	 ('2020-10-24 00:00:00'),
	 ('2020-10-24 00:00:00'),
	 ('2020-10-24 00:00:00'),
	 ('2021-03-12 23:30:25');
