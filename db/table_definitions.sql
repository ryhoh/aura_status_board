--------------------
-- Table Definition
--------------------

-- DROP TABLE public.devices;
CREATE TABLE public.devices (
	device_id SERIAL NOT NULL,
	device_name VARCHAR(32) NOT NULL,
	last_heartbeat TIMESTAMP(0) NULL,
	return_message VARCHAR(4096) NULL,
	has_gpu bool NOT NULL,
	CONSTRAINT devices_pk PRIMARY KEY (device_id),
	CONSTRAINT devices_un UNIQUE (device_name)
);

-- DROP TABLE public.gpu_machines;
CREATE TABLE public.gpu_machines (
	machine_id SERIAL NOT NULL,
	last_detail VARCHAR(4096) NOT NULL,
	CONSTRAINT gpu_machines_pk PRIMARY KEY (machine_id),
	CONSTRAINT gpu_machines_fk FOREIGN KEY (machine_id) REFERENCES public.devices(device_id) ON DELETE RESTRICT ON UPDATE RESTRICT
);


--------------------
-- Data Insertion
--------------------

INSERT INTO public.devices (device_name,last_heartbeat,has_gpu) VALUES
	('takenaka_dl',current_timestamp,true),
	('SMC101',current_timestamp,false),
	('AGP092',current_timestamp,true),
	('AGP093','2021-03-12 23:30:25',false);

INSERT INTO public.gpu_machines (machine_id,last_detail) VALUES
	(1,'testtesttest'),
	(3,'Mon Mar  8 21:37:43 2021
 -----------------------------------------------------------------------------
| NVIDIA-SMI 450.102.04   Driver Version: 450.102.04   CUDA Version: 11.0     |
|------------------------------- ---------------------- ---------------------- ');
