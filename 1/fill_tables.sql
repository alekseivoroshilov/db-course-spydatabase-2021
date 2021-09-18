INSERT INTO public.person (bio, name)
	VALUES 
	('1985, Portsmooth, England, fem.', 'Lucy Landa'),
	('1987, Kong Hong, China, mal.', 'Wei Shen'),
	('1983, Ryazan, USSR', 'Dmitry Tachankin'),
	('1990, Poland', 'Dober Lodvinof');

INSERT INTO public.unit_profile (info, person_id, date_from, date_to)
	VALUES
	('Good coordinator, knows 7 languages:..., the most young in agency', 1, '2006-05-15','2008-05-15'),
	('Excellent coordinator, knows 9 languages:...', 1, '2008-05-15', null),
	('Excellent integorator, knows 3 languages:...', 2, '2009-05-15', null),
	('Heavy weapons and explosives expert, 2 languages:...', 3, '2010-05-15', null),
	('Stealth expert, agent Colossus eliminated during mission "Sunset 2020-07-23"', 4, '2009-05-15', '2020-07-23');
	
INSERT INTO public.med_record (title, info, person_id, date_from, date_to)
	VALUES
	('Pneumonia', 'hard case', 1, '2010-05-15','2010-06-25'),
	('KIA', 'Bullet shot, blood loss', 4,'2020-03-20','2020-03-20');
	
INSERT INTO public.operator (info, unit_profile_id, available)
	VALUES
	('operations manager', 1, false);
	
INSERT INTO public.mission (name, rank, info, operator_id, mission_status)
	VALUES
	('Electric Vision', 3, 'Eliminate the general', 1, 'FINISHED'),
	('Rising Storm', 3, 'Rescue the diplomat', 1, 'PERFORMING'),
	('Sunset', 3, 'Lenetti mafia undercover', 1, 'FINISHED');
INSERT INTO public.pack (name, info)
	VALUES
	('Civilian disguise', 'civil concealment + hidden pistol'),
	('Killer loadout', 'handheld rifle + high tech jacket');

INSERT INTO public.item (name, info, pack_id)
	VALUES
	('classic suit', 'jacket+pants+shoes with camera and integrated telephone device', 1),
	('civilian suit', 'jacket+jeans+trainers with camera and integrated telephone device', 2),
	('Lady pistol', '2 shots, 45 cal., silenced', 1),
	('M21', 'Sniper rifle, silenced', 2),
	('Train ticket', 'from Stambul to Bagdat on 2020-07-08', 2);

INSERT INTO public.agent (name, rank, pack_id, unit_profile_id, available)
	VALUES
	('Blackbeard', 3, 1, 4, true),
	('Tiger', 3, 2, 3, false);
INSERT INTO public.agent_mission (agent_id, mission_id, info, date_from, date_to)
	VALUES
	(1, 2 , 'excellent chances, agent prepared and dislocated', '2020-07-08', '2020-08-15'),
	(2, 1 , 'high risk, dangerous mission', '2020-07-15', '2020-03-20');
	
INSERT INTO public.mission_result (mission_id, info, time)
	VALUES
	(1, 'Blackbeard aka Dmitry Tachankin [Blackbeard] has done his mission with success. General eliminated', DEFAULT),
	(2, 'Diplomat now being protected by Wei Chen [Tiger]', DEFAULT),
	(3, 'Agent Colossus [Dober Lodvinof] revealed by mafia and killed', DEFAULT),
	(3, 'Body of Agent Colossus [Dober Lodvinof] delivered to morgue', DEFAULT);
	
INSERT INTO public.loot (mission_result_id, rank, info, name)
	VALUES
	(1, 3, 'photos of mission process and result', 'evidences'),
	(2, 2, 'We confirmed the message from Tiger: diplomat being secured', 'message'),
	(4, 4, 'Corpse of the agent Colossus. Important information in usb-storage found inside his belly.', 'information');