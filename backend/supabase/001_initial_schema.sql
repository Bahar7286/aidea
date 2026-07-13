-- AgriTwin AI MVP schema (Supabase / PostgreSQL)
-- Rainfall lives on sensor_readings; no separate weather table.

create extension if not exists "pgcrypto";

create type source_type as enum ('manual', 'simulation', 'test_dataset');
create type risk_level as enum ('low', 'medium', 'high', 'critical');
create type irrigation_status as enum ('pending', 'running', 'completed', 'stopped');

create table if not exists users (
  id bigserial primary key,
  name varchar(120) not null,
  email varchar(255) not null unique,
  password_hash varchar(255) not null,
  role varchar(50) not null default 'farmer',
  created_at timestamptz not null default now()
);

create table if not exists farms (
  id bigserial primary key,
  user_id bigint not null references users(id) on delete cascade,
  name varchar(120) not null,
  location varchar(255),
  area double precision,
  soil_type varchar(80),
  irrigation_type varchar(80),
  created_at timestamptz not null default now()
);

create index if not exists idx_farms_user_id on farms(user_id);

create table if not exists crops (
  id bigserial primary key,
  farm_id bigint not null references farms(id) on delete cascade,
  crop_type varchar(80) not null,
  planting_date timestamptz,
  growth_stage varchar(80)
);

create index if not exists idx_crops_farm_id on crops(farm_id);

create table if not exists sensor_readings (
  id bigserial primary key,
  farm_id bigint not null references farms(id) on delete cascade,
  source_type source_type not null,
  timestamp timestamptz not null default now(),
  soil_moisture double precision not null check (soil_moisture >= 0 and soil_moisture <= 100),
  soil_temperature double precision,
  air_temperature double precision,
  air_humidity double precision check (air_humidity is null or (air_humidity >= 0 and air_humidity <= 100)),
  rainfall_probability double precision check (rainfall_probability is null or (rainfall_probability >= 0 and rainfall_probability <= 100)),
  ph double precision check (ph is null or (ph >= 0 and ph <= 14)),
  ec double precision,
  salinity double precision,
  last_irrigation_hours_ago double precision,
  irrigation_duration double precision,
  water_amount double precision,
  data_confidence double precision
);

create index if not exists idx_sensor_readings_farm_id on sensor_readings(farm_id);
create index if not exists idx_sensor_readings_timestamp on sensor_readings(timestamp desc);

create table if not exists predictions (
  id bigserial primary key,
  farm_id bigint not null references farms(id) on delete cascade,
  irrigation_needed boolean not null,
  irrigation_duration double precision,
  risk_level risk_level not null,
  confidence_score double precision not null,
  explanation text not null,
  moisture_24h double precision,
  moisture_48h double precision,
  moisture_72h double precision,
  created_at timestamptz not null default now()
);

create index if not exists idx_predictions_farm_id on predictions(farm_id);

create table if not exists irrigation_events (
  id bigserial primary key,
  farm_id bigint not null references farms(id) on delete cascade,
  start_time timestamptz not null default now(),
  end_time timestamptz,
  duration double precision,
  water_amount double precision,
  status irrigation_status not null default 'pending'
);

create index if not exists idx_irrigation_events_farm_id on irrigation_events(farm_id);

create table if not exists devices (
  id bigserial primary key,
  farm_id bigint not null references farms(id) on delete cascade,
  device_name varchar(120) not null,
  device_type varchar(80) not null,
  connection_status varchar(40) not null default 'active',
  last_data_time timestamptz,
  unique (farm_id, device_name)
);

create index if not exists idx_devices_farm_id on devices(farm_id);

-- Optional RLS helpers when using Supabase Auth (map auth.uid() later).
-- For JWT/backend-owned auth in MVP, API enforces farm ownership.
