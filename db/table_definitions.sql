--------------------
-- Table Definition
--------------------

CREATE TABLE public.devices (
	device_id SERIAL NOT NULL,
	device_name VARCHAR(32) NOT NULL,
	last_heartbeat TIMESTAMP(0) NULL,
	return_message VARCHAR(4096) NULL,
	has_gpu bool NOT NULL,
	CONSTRAINT devices_pk PRIMARY KEY (device_id),
	CONSTRAINT devices_un UNIQUE (device_name)
);

CREATE TABLE public.gpu_machines (
	machine_id SERIAL NOT NULL,
	last_detail VARCHAR(4096) NOT NULL,
	CONSTRAINT gpu_machines_pk PRIMARY KEY (machine_id),
	CONSTRAINT gpu_machines_fk FOREIGN KEY (machine_id) REFERENCES public.devices(device_id) ON DELETE RESTRICT ON UPDATE RESTRICT
);

CREATE TABLE public.jwt (
	secret VARCHAR(255) NOT NULL
);

CREATE TABLE public.users (
	user_name VARCHAR(16) NOT NULL,
	hashed_password BYTEA NOT NULL,
	CONSTRAINT users_pk PRIMARY KEY (user_name)
);


--------------------
-- Data Insertion
--------------------

INSERT INTO public.devices (device_name,last_heartbeat,has_gpu,return_message) VALUES
	('takenaka_dl',current_timestamp,true,NULL),
	('SMC101',current_timestamp,false,'Hello SMC!'),
	('AGP092',current_timestamp,true,'Loooooooooooooong message!'),
	('AGP093','2021-03-12 23:30:25',false,NULL);

INSERT INTO public.gpu_machines (machine_id,last_detail) VALUES
	(1,'testtesttest'),
	(3,'Mon Mar  8 21:37:43 2021
 -----------------------------------------------------------------------------
| NVIDIA-SMI 450.102.04   Driver Version: 450.102.04   CUDA Version: 11.0     |
|------------------------------- ---------------------- ---------------------- ');

INSERT INTO public.jwt VALUES
	('cc125635c56e2b29e842b7c520a5304eda31c3f0d409c09a911bcc5e742dcd60');

INSERT INTO public.users VALUES
	('ryhoh', '$2b$12$uWqI2KUFmu9j.FBetR0HGOiXYLeeTNWrlBq0skxYi2iHChhm35vT.');
