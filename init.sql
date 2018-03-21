-- init.sql
-- proj2
-- jake pasternak
-- cent 280
-- spr 2018

drop table if exists users cascade;

create table users (
	id serialm,
	first_name text,
	last_name text,
	username text,
	password text,
	salt text,
	enc_pass text,
	primary key (id)
);

