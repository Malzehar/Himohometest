-- Everything here will get rolled back at the end of a test run
-- Populate everything with known data

DELETE FROM doctors;
INSERT INTO doctors(id, first_name, last_name) VALUES (0, 'Testy', 'McTestFace');
INSERT INTO doctors(id, first_name, last_name) VALUES (1, 'Julius', 'Hibbert');

DELETE FROM locations;
INSERT INTO locations(id, address) VALUES (0, '1 Park St');
INSERT INTO locations(id, address) VALUES (1, '2 University Ave');

DELETE FROM doctor_locations;
INSERT INTO doctor_locations(id, doctor_id, location_id) VALUES (0, 0, 0);
INSERT INTO doctor_locations(id, doctor_id, location_id) VALUES (1, 0, 1);
INSERT INTO doctor_locations(id, doctor_id, location_id) VALUES (2, 1, 1);

DELETE FROM appointments;
INSERT INTO appointments(id, doctor_id, location_id, apmnt_time, is_canceled) VALUES (0,0,0,12,0);
INSERT INTO appointments(id, doctor_id, location_id, apmnt_time, is_canceled) VALUES (1,1,1,1558655106,0);

DELETE FROM doctor_hours;
INSERT INTO doctor_hours(id, doctor_id, shift_start, shift_end) VALUES (0,0,1560277403,1560320004);
INSERT INTO doctor_hours(id, doctor_id, shift_start, shift_end) VALUES (1,1,1557100801,1557104801);