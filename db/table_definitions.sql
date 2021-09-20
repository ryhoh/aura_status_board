--------------------
-- Table Definition
--------------------

CREATE TABLE public.devices (
	device_id SERIAL NOT NULL,
	device_name VARCHAR(32) NOT NULL,
	last_heartbeat TIMESTAMP(0) NULL,
	report VARCHAR(4096) DEFAULT '' NOT NULL,
	return_message VARCHAR(4096) DEFAULT '' NOT NULL,
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

INSERT INTO public.jwt VALUES
	('cc125635c56e2b29e842b7c520a5304eda31c3f0d409c09a911bcc5e742dcd60');

INSERT INTO public.users VALUES
	('ryhoh', '$2b$12$uWqI2KUFmu9j.FBetR0HGOiXYLeeTNWrlBq0skxYi2iHChhm35vT.');
