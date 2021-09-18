-- Вывести все миссии агентов, у которых средний результат выполнения миссий не хуже заданного. 
-- Все миссии FINISHED с агентами
WITH finished(aid, aname, mid, mstatus) AS (
	SELECT agent.agent_id AS aid, agent.name AS aname, mission.mission_id AS mid, mission.name AS mname,
	mission.mission_status AS mstatus
	FROM agent 
	JOIN agent_mission ON agent.agent_id = agent_mission.agent_id
	JOIN mission ON agent_mission.mission_id = mission.mission_id
	WHERE mission.mission_status = 'FINISHED'
	GROUP BY aid, mid
),


-- количество финишд миссий по каждому агенту
finishedct(aid, fins) AS (
	SELECT finished.aid AS aid, COUNT(mid) AS fins FROM finished
	GROUP BY finished.aid
),

-- Миссии каждого агента
allmissions(aid, aname, mid, mmstatus) AS (
	SELECT agent.agent_id AS aid, agent.name AS aname, mission.mission_id AS mid, mission.name AS mname,
	mission.mission_status AS mmstatus
	FROM agent 
	JOIN agent_mission ON agent.agent_id = agent_mission.agent_id
	JOIN mission ON agent_mission.mission_id = mission.mission_id
	GROUP BY aid, mid, mmstatus
),

-- count of all missions 4each agent
mct(aid, acnt) AS (
	SELECT am.aid as aid, COUNT(am.mid) AS acnt
	FROM allmissions am
	GROUP BY am.aid
)


SELECT am.aid, am.aname, am.mid, ms.mission_status, fc.fins AS fins, mct.acnt AS cnt, (fins/(mct.acnt+0.0)) as coef
FROM allmissions am 
JOIN finishedct fc ON fc.aid = am.aid
JOIN mct ON mct.aid = am.aid
JOIN mission ms ON ms.mission_id = am.mid

WHERE am.aid IN (
			SELECT aid from finished
)
GROUP BY am.aid, am.aname, am.mid, ms.mission_status, fins, mct.acnt
	HAVING (fins/(mct.acnt+0.0)) > 0.35
ORDER BY aid, fins DESC