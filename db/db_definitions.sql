--------------------
-- Role Definition
--------------------

-- DROP ROLE web;
CREATE ROLE web WITH 
	NOSUPERUSER
	NOCREATEDB
	NOCREATEROLE
	INHERIT
	LOGIN
	NOREPLICATION
	NOBYPASSRLS
	CONNECTION LIMIT -1;


--------------------
-- DataBase Definition
--------------------
CREATE DATABASE status_board WITH
	OWNER = web;
