CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE TABLE IF NOT EXISTS sensor_data (
    record_id BIGINT GENERATED ALWAYS AS IDENTITY NOT NULL, 
    device_id UUID NOT NULL, 
    record json NOT NULL, 
    created_t TIMESTAMP DEFAULT NOW()
    PRIMARY KEY (record_id)
);

CREATE TABLE IF NOT EXISTS devices (
    device_id UUID GENERATED ALWAYS AS IDENTITY NOT NULL DEFAULT uuid_generate_v4(),
    device_API_key CHAR[64] NOT NULL,
    created_t TIMESTAMP DEFAULT NOW(), 
    PRIMARY KEY (device_id)
);

CREATE TABLE IF NOT EXISTS experiments (
    experiment_id BIGINT GENERATED ALWAYS AS IDENTITY NOT NULL,
    device_id UUID NOT NULL,
    control_start
    control_duration
    test_start
    test_duration
    running     // 3 bits for XOR-ability to see control/ test/ complete 
    PRIMARY KEY (experiment_id)
);