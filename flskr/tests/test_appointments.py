import time
import json

def test_get_all_doctor_appointments(client):
    # Test getting all doctor appointment by doctor ID
    rv = client.get('/doctors/appointment/0')
    assert rv.status_code == 200

    # Can't guarantee order, so test that we get the expected count and fields seem to make sense
    data = json.loads(rv.data)
    assert len(data) == 1
    for field in ['address', 'apmnt_time', 'first_name', 'last_name']:
        assert field in data[0]

def test_add_work_hours(client):
    # Test adding doctor work hours, successfully

    # Note: Flask chokes if you pass in an inline dict; must use json.dumps()
    rv = client.post('/doctor/schedule/set',
        data=json.dumps(dict(doctor_id='0', shift_start="1560276124", shift_end="1560318824")),
        content_type='application/json')

    assert rv.status_code == 200

    data = json.loads(rv.data)
    assert data['shift start / end ID: '] == 2


def test_schedule_appointment(client):
    # Test scheduling an appointment, successfully

    rv = client.post('/doctors/appointment',
                     data=json.dumps(dict(doctor_id='0', location_id='0', apmnt_time='1560298281')),
                     content_type='application/json')

    assert rv.status_code == 200

    data = json.loads(rv.data)
    assert data['Appointment ID: '] == 2


#This should come after an appointment is scheduled...?
def test_get_all_doctor_shedule(client):
    # Test getting all doctor appointment and work hours by doctor ID, successfully.
    # returns two lists, shift start / end list, and appointment time list.
    rv = client.get('/doctors/weekly_schedule/0')
    assert rv.status_code == 200

    
    # Can't guarantee order, so test that we get the expected count and fields seem to make sense
    data = json.loads(rv.data)
    assert len(data) == 2
    for field in [['shift_start', 'shift_end'], ['apmnt_time']]:
        assert field in data[0]


'''
def test_get_valid_doctor(client):
    # Test getting a single doctor, successfully
    rv = client.get('/doctors/0')
    assert rv.status_code == 200

    data = json.loads(rv.data)
    assert data['id'] == 0
    assert data['first_name'] == 'Testy'
    assert data['last_name'] == 'McTestFace'


def test_get_invalid_doctor(client):
    # Test getting a single doctor that doesn't exist
    rv = client.get('/doctors/2')
    assert rv.status_code == 400


def test_create_doctor(client):
    # Test creating a real doctor, successfully

    # Note: Flask chokes if you pass in an inline dict; must use json.dumps()
    rv = client.post('/doctors',
                     data=json.dumps(dict(first_name='Elmer', last_name='Hartman')),
                     content_type='application/json')

    assert rv.status_code == 200

    data = json.loads(rv.data)
    assert data['id'] == 2


def test_create_invalid_doctor(client):
    # Test various ways a doctor creation may fail
    rv = client.post('/doctors',
                     data=json.dumps(dict(first_name='Elmer')),
                     content_type='application/json')

    assert rv.status_code == 400

    data = json.loads(rv.data)
    assert data['error_detail'] == 'Missing required field'

    rv = client.post('/doctors',
                     data=json.dumps(dict(last_name='Hartman')),
                     content_type='application/json')

    assert rv.status_code == 404

    data = json.loads(rv.data)
    assert data['error_detail'] == 'Missing required field'



'/doctors/appointment/cancel'
'/doctors/appointment'
#'/doctor/schedule/set'
'''