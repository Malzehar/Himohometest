-- Initialize the database.
-- Drop any existing data and create empty tables.

DROP TABLE IF EXISTS doctors;
DROP TABLE IF EXISTS locations;
DROP TABLE IF EXISTS doctor_locations;
DROP TABLE IF EXISTS appointments;
DROP TABLE IF EXISTS doctor_hours;

CREATE TABLE doctors (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  first_name TEXT NOT NULL,
  last_name TEXT NOT NULL
);

CREATE TABLE locations (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  address TEXT NOT NULL
);

CREATE TABLE doctor_locations (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  doctor_id INTEGER NOT NULL,
  location_id INTEGER NOT NULL,
  FOREIGN KEY (doctor_id) REFERENCES doctors (id),
  FOREIGN KEY (location_id) REFERENCES locations (id)
);

CREATE TABLE appointments (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  day_stamp INTEGER NOT NULL,
  doctor_id INTEGER NOT NULL,
  location_id INTEGER NOT NULL,
  apmnt_time INTEGER NOT NULL,
  is_canceled INTEGER NOT NULL,
  FOREIGN KEY (doctor_id) REFERENCES doctors (id),
  FOREIGN KEY (location_id) REFERENCES locations (id)
);

CREATE TABLE doctor_hours(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  day_stamp INTEGER NOT NULL,
  doctor_id INTEGER NOT NULL,
  shift_start INTEGER NOT NULL,
  shift_end INTEGER NOT NULL,
  FOREIGN KEY (doctor_id) REFERENCES doctors (id)
);


INSERT INTO doctors(id, first_name, last_name) VALUES (0, 'John', 'Doe');
INSERT INTO doctors(id, first_name, last_name) VALUES (1, 'Jane', 'Smith');

INSERT INTO locations(id, address) VALUES (0, '123 Main St');
INSERT INTO locations(id, address) VALUES (1, '456 Central St');

INSERT INTO doctor_locations(id, doctor_id, location_id) VALUES (0, 0, 0);
INSERT INTO doctor_locations(id, doctor_id, location_id) VALUES (1, 1, 0);
INSERT INTO doctor_locations(id, doctor_id, location_id) VALUES (2, 1, 1);

INSERT INTO appointments(id, day_stamp, doctor_id, location_id, apmnt_time, is_canceled) VALUES (0,1561089600, 0,0,1561136809,0);
INSERT INTO appointments(id, day_stamp, doctor_id, location_id, apmnt_time, is_canceled) VALUES (1,1561089600,0,0,1561137209,0);
INSERT INTO appointments(id, day_stamp, doctor_id, location_id, apmnt_time, is_canceled) VALUES (2,1558569600,1,1,1558655106,0);
INSERT INTO appointments(id, day_stamp, doctor_id, location_id, apmnt_time, is_canceled) VALUES (3,99999360000,0,0,9999999999,0);

INSERT INTO doctor_hours(id, day_stamp, doctor_id, shift_start, shift_end) VALUES (0,1561089600,0,1561133209,1561176409);
INSERT INTO doctor_hours(id, day_stamp, doctor_id, shift_start, shift_end) VALUES (1,1561089600,1,1557100801,1557104801);