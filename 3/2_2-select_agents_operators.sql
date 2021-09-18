-- Удалить из миссий агентов, которые являются операторами в этих миссиях.

-- выбираем unit_profile, где agent_id и operator_id не NULL
WITH up(aid, oid) AS (
	SELECT agent_id AS aid, operator_id AS oid
	FROM unit_profile
	WHERE agent_id IS NOT NULL AND operator_id IS NOT NULL
	GROUP BY agent_id, operator_id
),

-- все миссии, со всеми причисленными к ним агентами, но в миссиях оператор относится к личному делу, где есть агент.
-- кроме того, вы этом запросе есть учёт назначения на миссию.
	
allmissions(mid, oid, op_agent, aid) AS (
	SELECT mission.mission_id AS mid, mission.operator_id AS oid,
	up.aid as op_agent, am.agent_id AS aid
	FROM mission
	JOIN up ON up.oid = mission.operator_id
	JOIN agent_mission am ON am.mission_id = mission.mission_id
	WHERE mission.operator_id IN (
		SELECT oid FROM up
	)
	
	GROUP BY mission.mission_id, mission.operator_id,  am.agent_id, up.aid
)

--select missions where operators are inlisted in those missions as agent 
SELECT allmissions.mid, allmissions.oid, allmissions.op_agent, allmissions.aid
FROM allmissions
WHERE allmissions.op_agent = allmissions.aid
GROUP BY allmissions.mid, allmissions.oid, allmissions.op_agent, allmissions.aid
ORDER BY allmissions.mid

-- SELECT missions, agents, operators, ops-agents,
-- next -> SELECT ops-agents WHERE ops-agent = agent
