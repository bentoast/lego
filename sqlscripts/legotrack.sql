SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: legotrack; Type: TABLE; Schema: public; Owner: lego
--

CREATE TABLE public.legotrack (
    setid integer,
    userid integer,
    track boolean,
    have boolean
);


ALTER TABLE public.legotrack OWNER TO lego;