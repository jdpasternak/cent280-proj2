-- auth_funcs.sql
drop function if exists do_hash(text);
drop function if exists make_salt(text);
drop function if exists make_enc_pass(text);
drop function if exists add_user(text,text,text,text);
drop function if exists check_id(text,text);


create function do_hash(_text text)
   returns text as
   $$
      begin
         return encode(digest(_text,'sha512'),'hex');
      end;
   $$
   language 'plpgsql';

create function make_salt(_text text)
   returns text as
   $$
      begin
         return do_hash(now() || _text);
      end;
   $$
   language 'plpgsql';

create function make_enc_pass(_text text)
   returns text as
   $$
      begin
         return do_hash(_text || make_salt(_text));
      end;
   $$
   language 'plpgsql';

create function add_user(_fn text, _ln text, _user text, _pass text)
   returns integer as
   $$
      declare
         rec record;
         _user_id integer;
      begin
         select * into rec from users where username=_user;
         if not found then
            insert into users (first_name, last_name, username,
               salt, enc_pass) values (_fn, _ln, _user, 
               make_salt(_pass), make_enc_pass(_pass));
            _user_id := currval('users_id_seq');
         else
            _user_id := rec.id;
         end if;
         return _user_id;
      end;
   $$
   language 'plpgsql';

create function check_id(_user text, _pass text)
   returns integer as
   $$
      declare
         rec record;
         _user_id integer;
      begin
         select * into rec from users where username=_user;
         if not found then
            return -1;
         else
            if (do_hash(_pass || rec.salt) = rec.enc_pass) then
               return rec.id;
            else
               return -1;
            end if;
         end if;
      end;
   $$
   language 'plpgsql';
