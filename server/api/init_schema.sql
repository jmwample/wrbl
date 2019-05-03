CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE TABLE IF NOT EXISTS sensor_data (
    record_id BIGINT GENERATED ALWAYS AS IDENTITY NOT NULL, 
    device_id UUID NOT NULL, 
    record json NOT NULL, 
    created_t TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (record_id)
);

CREATE TABLE IF NOT EXISTS devices (
    device_id UUID DEFAULT uuid_generate_v4() UNIQUE,
    device_API_key CHAR(64) NOT NULL,
    created_t TIMESTAMP DEFAULT NOW(), 
    PRIMARY KEY (device_id)
);


CREATE TABLE IF NOT EXISTS experiments (
    experiment_id BIGINT GENERATED ALWAYS AS IDENTITY NOT NULL,
    device_id UUID NOT NULL,
    ctrl_start TIMESTAMP DEFAULT NOW(),
    ctrl_end TIMESTAMP,
    ctrl_dur INTERVAL,
    test_start TIMESTAMP,
    test_end TIMESTAMP,
    test_dur INTERVAL,
    fields BIGINT [],
    labels BIGINT [],
    graph_path TEXT,
    status SMALLINT DEFAULT 0,
    PRIMARY KEY (experiment_id)
);

CREATE TABLE IF NOT EXISTS fields (
    field_id BIGINT GENERATED ALWAYS AS IDENTITY NOT NULL,
    letter CHAR(1) NOT NULL,
    name VARCHAR (32) NOT NULL,
    description TEXT,
    PRIMARY KEY (field_id)
);

CREATE TABLE IF NOT EXISTS labels (
    label_id BIGINT GENERATED ALWAYS AS IDENTITY NOT NULL,
    label VARCHAR (32) NOT NULL UNIQUE,
    PRIMARY KEY (label_id)
);

CREATE TABLE IF NOT EXISTS results (
    result_id BIGINT GENERATED ALWAYS AS IDENTITY NOT NULL,
    experiment_id BIGINT NOT NULL,
    response BOOLEAN NOT NULL,
    graph_path TEXT,
    PRIMARY KEY (result_id)    
);


/*==================[ Debug inserts to analyze usability ]==================*/

/*
INSERT INTO devices (device_id, device_API_key) 
VALUES 
    ('6829cb99-d81c-4823-bca6-bbdd3ddaf527', 
     'QBWTNdHn2l7S5eqcvRqr61X6kArLiFSuqKF8XdOj7sf5cDNGglqLlIZH54HEs2Dw'); 


INSERT INTO labels (label) 
VALUES
    ('debug'),
    ('jack'),
    ('state_of_the_union');
INSERT INTO fields (letter, name) 
VALUES
    ('h', 'Heart Rate'),
    ('g', 'Galvanic Skin Response'),
    ('t', 'Body Temperature'),
    ('x', 'Acceleration - X'),
    ('y', 'Acceleration - Y'),
    ('z', 'Acceleration - Z');
INSERT INTO experiments (device_id, ctrl_start, ctrl_end, ctrl_dur, test_start, test_end, test_dur, labels, fields, graph_path, status)
VALUES 
    ('6829cb99-d81c-4823-bca6-bbdd3ddaf527', NOW(), NOW() + interval '30 seconds', interval '30 seconds',
     NOW()+interval '30 seconds', NOW() + interval '40 seconds', interval '10 seconds', ARRAY [1,2], ARRAY [1,2,3,4,5,6], 
     '/static/images/full_graph.png', 4),
    ('6829cb99-d81c-4823-bca6-bbdd3ddaf527', NOW(), NOW() + interval '10 years', interval '10 years',
     NOW()+interval '10 years', NOW() + interval '10 years' + interval '10 seconds', interval '10 seconds', ARRAY [1,2], ARRAY [1,2,3,4,5,6], 
     '/static/images/full_graph.png', 1),
    ('6829cb99-d81c-4823-bca6-bbdd3ddaf527', NOW(), NOW() + interval '30 seconds', interval '30 seconds',
     NOW()+interval '30 seconds', NOW() + interval '10 years' + interval '30 seconds', interval '10 years', ARRAY [1,2], ARRAY [1,2,3,4,5,6],
     '/static/images/full_graph.png', 2),
    ('5d910814-2804-4dd9-ae18-5acb2f18ced3', NOW(), NOW() + interval '30 seconds', interval '30 seconds',
     NOW()+interval '30 seconds', NOW() + interval '40 seconds', interval '10 seconds', ARRAY [1,2], ARRAY [1,2,3,4,5,6],
     '/static/images/full_graph.png', 4);

INSERT INTO results (experiment_id, response, graph_path)
VALUES
    (1, TRUE, '/static/images/full_graph.png'),
    (4, FALSE, '/static/images/full_graph.png');
*/

