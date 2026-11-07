-- Solar generation analytics schema (SQLite). All data loaded by seed.py is synthetic.
DROP TABLE IF EXISTS plants;
DROP TABLE IF EXISTS irradiance_daily;
DROP TABLE IF EXISTS generation_daily;
DROP TABLE IF EXISTS meter_monthly;

CREATE TABLE plants (
    plant_id        TEXT PRIMARY KEY,
    name            TEXT NOT NULL,
    plant_type      TEXT NOT NULL,          -- rooftop | ground-mount
    dc_kwp          REAL NOT NULL,          -- module capacity
    ac_kw           REAL NOT NULL,          -- inverter capacity
    cod_date        TEXT NOT NULL,          -- commercial operation date
    tariff_inr_kwh  REAL NOT NULL           -- PPA tariff billed per metered unit
);

CREATE TABLE irradiance_daily (            -- plane-of-array irradiation from the site sensor
    plant_id    TEXT REFERENCES plants(plant_id),
    day         TEXT NOT NULL,
    poa_kwh_m2  REAL NOT NULL,
    PRIMARY KEY (plant_id, day)
);

CREATE TABLE generation_daily (            -- inverter (SCADA) energy, AC side
    plant_id      TEXT REFERENCES plants(plant_id),
    day           TEXT NOT NULL,
    inverter_kwh  REAL NOT NULL,
    PRIMARY KEY (plant_id, day)
);

CREATE TABLE meter_monthly (               -- billing meter, the number the invoice uses
    plant_id    TEXT REFERENCES plants(plant_id),
    month       TEXT NOT NULL,             -- YYYY-MM
    meter_kwh   REAL NOT NULL,
    PRIMARY KEY (plant_id, month)
);
