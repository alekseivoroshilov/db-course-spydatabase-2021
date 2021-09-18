-- Удалить из миссий агентов, которые являются операторами в этих миссиях.
-- select all unit_profiles where agent and operator is not null
WITH up(aid, oid) AS (
	SELECT agent_id AS aid, operator_id AS oid
	FROM unit_profile
	WHERE agent_id IS NOT NULL AND operator_id IS NOT NULL
	GROUP BY agent_id, operator_id
),


-- select all missions AND their agents, 
-- where operator is an agent + agent_id as op_agent for those operators
	
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
),

--select missions where operators are in those missions agent lists
deletefun(mid, oid, opaid, aid) AS (
	SELECT allmissions.mid AS mid, allmissions.oid AS oid, allmissions.op_agent AS opaid, allmissions.aid AS aid
	FROM allmissions
	WHERE allmissions.op_agent = allmissions.aid
	GROUP BY allmissions.mid, allmissions.oid, allmissions.op_agent, allmissions.aid
	ORDER BY allmissions.mid
)

DELETE FROM agent_mission 
WHERE agent_mission.agent_id 
IN (
	SELECT aid FROM deletefun
)


-- SELECT missions, agents, operators, ops-agents,
-- next -> SELECT ops-agents WHERE ops-agent = agent