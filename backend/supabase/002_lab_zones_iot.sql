-- P1: management zones, lab reports, dual-depth moisture, iot source types

-- Extend source_type if using Postgres enums (run carefully on existing DBs)
-- alter type source_type add value if not exists 'lab_report';
-- alter type source_type add value if not exists 'lab_manual';
-- alter type source_type add value if not exists 'iot';

do $$ begin
  create type lab_source_type as enum ('lab_report', 'lab_manual');
exception when duplicate_object then null;
end $$;

create table if not exists management_zones (
  id bigserial primary key,
  farm_id bigint not null references farms(id) on delete cascade,
  name varchar(120) not null,
  notes text,
  created_at timestamptz not null default now(),
  unique (farm_id, name)
);

create index if not exists idx_management_zones_farm_id on management_zones(farm_id);

create table if not exists lab_reports (
  id bigserial primary key,
  farm_id bigint not null references farms(id) on delete cascade,
  zone_id bigint references management_zones(id) on delete set null,
  lab_name varchar(160) not null,
  report_number varchar(80),
  analysis_date timestamptz,
  sample_date timestamptz,
  sample_depth_cm varchar(40),
  sample_region varchar(120),
  file_name varchar(255),
  source_type lab_source_type not null,
  user_confirmed boolean not null default false,
  notes text,
  created_at timestamptz not null default now()
);

create index if not exists idx_lab_reports_farm_id on lab_reports(farm_id);

create table if not exists lab_parameters (
  id bigserial primary key,
  report_id bigint not null references lab_reports(id) on delete cascade,
  parameter_code varchar(40) not null,
  value double precision not null,
  unit varchar(40) not null,
  method varchar(80),
  extracted_auto boolean not null default false
);

create index if not exists idx_lab_parameters_report_id on lab_parameters(report_id);

alter table sensor_readings
  add column if not exists zone_id bigint references management_zones(id) on delete set null,
  add column if not exists soil_moisture_deep double precision,
  add column if not exists moisture_depth_cm double precision,
  add column if not exists moisture_deep_depth_cm double precision,
  add column if not exists is_validated boolean not null default true,
  add column if not exists device_id bigint references devices(id) on delete set null;
