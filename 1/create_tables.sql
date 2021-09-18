START TRANSACTION;


CREATE TYPE public.mission_status AS ENUM ('PLANNING', 'STARTING', 'PERFORMING', 'CANCELLING', 'FINISHED');


CREATE TABLE IF NOT EXISTS public.person
(
    person_id serial      not null
        constraint person_file_pk
            primary key,
    bio       text,
    name      varchar(50) not null
);


CREATE TABLE IF NOT EXISTS public.med_record
(
    med_record_id serial      not null
        constraint status_pk
            primary key,
    title         varchar(30) not null,
    info          text,
    person_id     integer     not null
        constraint med_record_person_person_id_fk
            references public.person
            on update cascade on delete cascade,
    date_from     date        not null,
    date_to       date
);


CREATE TABLE IF NOT EXISTS operator
(
    operator_id serial               not null
        constraint person_pk
            primary key,
    info        text,
    available   boolean default true not null
);




CREATE TABLE IF NOT EXISTS public.mission
(
    mission_id     serial                                                                    not null
        constraint mission_type_pk
            primary key,
    name           varchar(50)                                                               not null,
    rank           integer                                                                   not null,
    info           text,
    operator_id    integer
        constraint mission_operator_operator_id_fk
            references public.operator
            on update cascade on delete set null,
    mission_status public.mission_status default 'PLANNING'::public.mission_status not null
);


CREATE TABLE IF NOT EXISTS public.pack
(
    pack_id serial      not null
        constraint pack_pk
            primary key,
    name    varchar(50) not null,
    info    text
);


CREATE TABLE IF NOT EXISTS agent
(
    agent_id  serial               not null
        constraint agend_bio_pk
            primary key,
    name      varchar(50)          not null,
    available boolean default true not null,
    pack_id   integer
        constraint agent_pack_id_fkey
            references pack
);


CREATE TABLE IF NOT EXISTS unit_profile
(
    unit_profile_id serial  not null
        constraint unit_profile_pk
            primary key,
    info            text,
    rank            integer not null,
    person_id       integer not null
        constraint unit_profile_person_person_id_fk
            references person
            on update cascade on delete cascade,
    date_from       date    not null,
    date_to         date,
    agent_id        integer
        constraint unit_profile_agent_agent_id_fk_2
            references agent
            on update cascade on delete cascade,
    operator_id     integer
        constraint unit_profile_operator_operator_id_fk
            references operator
            on update cascade on delete cascade
);


CREATE TABLE IF NOT EXISTS public.agent_mission
(
    agent_mission_id serial  not null
        constraint agent_mission_pk
            primary key,
    agent_id         integer not null
        constraint agent_mission_agents_agent_id_fk
            references public.agent
            on update cascade,
    mission_id       integer not null
        constraint agent_mission_mission_mission_id_fk
            references public.mission
            on update cascade on delete cascade,
    info             text,
    date_from        date    not null,
    date_to          date
);


CREATE TABLE IF NOT EXISTS public.mission_result
(
    mission_result_id serial                    not null
        constraint mission_result_pk
            primary key,
    mission_id        integer                   not null
        constraint mission_result_mission_mission_id_fk
            references public.mission
            on update cascade on delete cascade,
    info              text,
    time              varchar(30) default now() not null
);


CREATE TABLE IF NOT EXISTS public.loot
(
    loot_id           serial      not null
        constraint loot_pk
            primary key,
    mission_result_id integer     not null
        constraint intel_mission_result_mission_result_id_fk
            references public.mission_result
            on update cascade on delete cascade,
    rank              integer     not null,
    info              text,
    name              varchar(50) not null
);


CREATE TABLE IF NOT EXISTS public.item
(
    item_id serial      not null
        constraint item_pk
            primary key,
    name    varchar(50) not null,
    info    text,
    pack_id integer     not null
        constraint item_pack_pack_id_fk
            references public.pack
            on update cascade on delete set null
);

COMMIT;