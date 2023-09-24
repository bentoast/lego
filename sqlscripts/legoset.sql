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
-- Name: legoset; Type: TABLE; Schema: public; Owner: lego
--

CREATE TABLE public.legoset (
    setid integer NOT NULL,
    name character varying(255) NOT NULL,
    price numeric(8,2) DEFAULT NULL::numeric,
    originalprice numeric(8,2) DEFAULT NULL::numeric,
    discount numeric(5,4) DEFAULT NULL::numeric,
    retiring boolean NOT NULL,
    new boolean NOT NULL,
    modified timestamp without time zone,
    cancheck boolean DEFAULT true
);


ALTER TABLE public.legoset OWNER TO lego;

--
-- Name: legoset legoset_pkey; Type: CONSTRAINT; Schema: public; Owner: lego
--

ALTER TABLE ONLY public.legoset
    ADD CONSTRAINT legoset_pkey PRIMARY KEY (setid);
