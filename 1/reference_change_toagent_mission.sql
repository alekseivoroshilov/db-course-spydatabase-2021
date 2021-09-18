ALTER TABLE agent_mission
ADD pack_id INT NULL;

ALTER TABLE agent_mission
ADD FOREIGN KEY(pack_id) REFERENCES pack(pack_id);

INSERT INTO agent_mission(pack_id) 
SELECT pack_id FROM agent;

ALTER TABLE agent
DROP COLUMN pack_id;