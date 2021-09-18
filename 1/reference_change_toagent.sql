ALTER TABLE agent
ADD pack_id INT NULL;

ALTER TABLE agent
ADD FOREIGN KEY(pack_id) REFERENCES pack(pack_id);

INSERT INTO agent(pack_id) 
SELECT pack_id FROM agent_mission;

ALTER TABLE agent_mission
DROP COLUMN pack_id;