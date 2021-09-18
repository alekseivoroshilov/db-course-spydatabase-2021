--Задание: Вывести агентов, которые никогда не участвовали в миссиях, где не были добыты луты.

--все миссии с mission_result, лутами, агентами
WITH mss(mid, mrid, lid, aid) AS (
    SELECT mission.mission_id, mr.mission_result_id, loot.loot_id, agent.agent_id
    FROM mission
    JOIN mission_result mr ON mr.mission_id = mission.mission_id
    JOIN loot on loot.mission_result_id = mr.mission_result_id
    JOIN agent_mission am ON am.mission_id = mission.mission_id
    JOIN agent ON agent.agent_id = am.agent_id
    GROUP BY mission.mission_id, mr.mission_result_id, loot.loot_id, agent.agent_id
),

--агенты и миссии, где хотя бы однажды лут не был получен
nolootags(aid, mid) AS (
    SELECT agent.agent_id, mission.mission_id
    FROM mission
    JOIN agent_mission ON agent_mission.mission_id = mission.mission_id
    JOIN agent ON agent.agent_id = agent_mission.agent_id
    WHERE mission.mission_id NOT IN 
    (SELECT mid FROM mss)
    GROUP BY  mission.mission_id, agent.agent_id
)

SELECT agent.agent_id, agent.name, mission.mission_id
FROM agent
JOIN agent_mission ON agent_mission.agent_id = agent.agent_id
JOIN mission on mission.mission_id = agent_mission.mission_id
WHERE agent.agent_id NOT IN (SELECT aid FROM nolootags)
ORDER BY agent.agent_id
