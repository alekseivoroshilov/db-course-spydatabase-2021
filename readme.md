# Spy Agency Database

База данных из 11 таблиц для хранения информации на тему выдуманного Шпионского агенства с целью изучения и выполнения заданий по курсу баз данных СПбПУ ИКНТ.

Выполнил студент:
>Ворошилов Алексей 
3530901/70203

# Описание таблиц
### person 
- Информация личного характера о всех работниках агенства

person_id | PK | (ключ)
--- | --- | ---
bio | text | биография человека
name | varchar(50) | имя человека
### unit_profile 
- Кратко говоря, профессиональное досье/портфолио. 
- Информация и легенда текущего и прошедших рангов, которые были у работника (какие звания в какой период носил, какие навыки способствовали ношению такого звания). 

unit_profile_id | PK | (ключ)
--- | --- | ---
info | text | отличительные качества в конкретный период
rank | integer | текущий ранг (1 - самый высокий)
person_id | integer(FK) | id человека (UP:cascade DEL:cascade)
date_from | date | начало работы на текущем звании
date_to | date | конец работы на текущем звании (если повышение - новая запись)
agent_id | integer(FK) | ID агента, у которого такое личное дело
operator_id | integer(FK) | ID оператора, у которого такое личное дело
### med_record
- Состояние здоровья работника в определенный период.

med_record_id | PK | (ключ)
--- | --- | ---
title | varchar(30) | название заболевания или состояния
info | text | дополнительная информация
person_id | integer(FK) | id пациента (UP:cascade DEL:cascade)
date_from | date | начало болезни/состояния
date_to | date | конец болезни/состояния
### operator
- Работники такого вида, которые руководят миссией или координируют её.

operator_id | PK | (ключ)
--- | --- | ---
info | text | дополнительная информация
unit_profile_id | integer(FK) | id текущего портфолио оператора (UP:no action DEL:set null)
available | boolean | Доступен в текущий момент? (default: true)

### mission
- Миссия, её состояние, назначенный оператор, и описание.
- mission_status является enum со следующими значениями: 'PLANNING', 'STARTING', 'PERFORMING', 'CANCELLING', 'FINISHED'

mission_id | PK | (ключ)
--- | --- | ---
name | varchar(50) | название
rank | integer | требуемый ранг (сложность) (1 - для самых лучших агентов и операторов)
info | text | особенности работы в конкретный период
operator_id | integer(FK) | id оператора, назначенного на миссию (UP:cascade DEL:cascade)
mission_status | enum | статус текущей миссии
### pack
- Такой набор вещей (множество item), который берёт с собой на задание один агент.

pack_id | PK | (ключ)
--- | --- | ---
name | varchar(50) | название набора снаряжения
info | text | доп. информация о снаряжении, включенном в набор
### item
- Любая вещь, костюм, гаджет, оружие. Может и человек, не работающий в текущем агенстве(заложник, переводчик).

unit_profile_id | PK | (ключ)
--- | --- | ---
name | varchar(50) | название гаджета или другого предмета агенства
info | text | особенности работы в конкретный период
pack_id | integer(FK) | id набора снаряжения, в котором этот предмет находится (UP:cascade DEL:set null)
### agent
- Агент, у которого имеется звание, ссылка на текущее портфолио, а также отображается доступность найма на текущий момент. (Например, если агент болеет, то available должно быть присвоено false)

agent_id | PK | (ключ)
--- | --- | ---
name | varchar(50) | имя/позывной агента
rank | integer | ранг агента (1 - лучший)
pack_id | integer(FK) | id набора снаряжения, которым пользуется агент (UP:set null DEL:set null)
unit_profile_id | integer(FK) | id досье агента (UP:no action DEL:set null)
available | boolean | Доступен в текущий момент? (default: true)
### agent_mission
- Отношение агента и миссии, описывающее на какой период был нанят агент на задание, а также дополнительная информация про выполненное содействие. По факту, история операций у агента.

agent_mission_id | PK | (ключ)
--- | --- | ---
agent_id | integer(FK) | id агента (UP:cascade DEL: no action)
mission_id | integer(FK) | id миссии (UP:cascade DEL:cascade)
info | text | дополнительная информация по назначению агента на миссию
date_from | date | когда был назначен на миссию
date_to | date | когда покинул/выполнил миссию

### mission_result
- Результат выполнения миссии. Результатов может быть много, например, в поэтапных миссиях.

mission_result_id | PK | (ключ)
--- | --- | ---
mission_id | integer(FK) | id миссии (UP:cascade DEL:cascade)
info | text | сводка о выполненнении миссии.
time | timestamp(without time zone) | (DEFAULT: now()) дата и время данного результата миссии.
### loot
- Информация о вещах или информации, добытой на опредённой стадии миссии (mission_result). loot (англ. добыча), также может указывать на человека: преступник, спасённая жертва, привлечённый двойной агент

loot_id | PK | (ключ)
--- | --- | ---
mission_result_id | integer(FK) | id сводки миссии, выполненной полностью или частично (UP:cascade DEL:cascade)
rank | integer | требуемый ранк работника/агента для доступа к информации
info | text | описание добытой информации, результата, предмета, кода
name | varchar(50) | краткое название или обозначение добытого на миссиии объекта или информации
# Вывод и ссылки
Представленные таблицы по задумке должны отражать основные процессы в шпионском бюро. 

>Telegram: @mermaider
>e-mail: voroshilov.aa@edu.spbstu.ru