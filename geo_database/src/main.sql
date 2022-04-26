
CREATE TABLE states(
    cve SMALLINT PRIMARY KEY,
    name_ VARCHAR(50)
);

CREATE TABLE municipialities(
    cve SERIAL PRIMARY KEY,
    name_ VARCHAR(100),
    state_cve SMALLINT REFERENCES states(cve),
    hash_name  VARCHAR(256)
);


CREATE TABLE municipialities_center(
    cve SERIAL PRIMARY KEY,
    municipialitie_cve SMALLINT REFERENCES municipialities(cve),
    lat_center NUMERIC,
    lng_center NUMERIC
);