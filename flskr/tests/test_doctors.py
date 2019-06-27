import json

def test_get_all_doctors(client):
    # Test that getting all doctors truly gets them all
    rv = client.get('/doctors')
    assert rv.status_code == 200

    # Can't guarantee order, so test that we get the expected count and fields seem to make sense
    data = json.loads(rv.data)
    assert len(data) == 2
    for field in ['id', 'first_name', 'last_name']:
        assert field in data[0]


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
    assert rv.status_code == 404


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

    assert rv.status_code == 400

    data = json.loads(rv.data)
    assert data['error_detail'] == 'Missing required field'


def test_doctor_update(client):
    # Test updating an existing doctor, successfully

    rv = client.post('/doctors/update',
        data=json.dumps(dict(doctor_id="0", first_name='Buggs', last_name='Bunny')),
        content_type='application/json')
    assert rv.status_code == 200

    data = json.loads(rv.data)
    assert data['id'] == 0
    assert data['first_name'] == 'Buggs'
    assert data['last_name'] == 'Bunny'


def test_invalid_doctor_update(client):
    # Test various ways a doctor updates may fail
    rv = client.post('/doctors/update',
        data=json.dumps(dict(doctor_id='3', first_name='Guy')),
        content_type='application/json')

    assert rv.status_code == 400

    data = json.loads(rv.data)
    assert data['error_detail'] == 'Missing required field(s)'

    rv = client.post('/doctors/update',
        data=json.dumps(dict(doctor_id='3', last_name='Fuierri')),
        content_type='application/json')

    assert rv.status_code == 400

    data = json.loads(rv.data)
    assert data['error_detail'] == 'Missing required field(s)'

    rv = client.post('/doctors/update',
        data=json.dumps(dict(first_name='Guy', last_name='Fuierri')),
        content_type='application/json')

    assert rv.status_code == 400

    data = json.loads(rv.data)
    assert data['error_detail'] == 'Missing required field(s)'

    rv = client.post('doctors/update',
        data=json.dumps(dict(doctor_id='9999999999999', first_name='Guy', last_name='Fuierri')),
        content_type='applicaiton/json')

    assert rv.status_code == 404

    #data = json.loads(rv.data)
    #assert data['error_detail'] == "SyntaxError: invalid syntax"


def test_doctor_delete(client):
    # Test deleting an existing doctor, successfully

    rv = client.post('/doctors/delete',
        data=json.dumps(dict(doctor_id="1")),
        content_type='application/json')
    assert rv.status_code == 200

    data = json.loads(rv.data)
    assert data["Removed doctor with ID: "] == '1'


def test_invalid_doctor_delete(client):
    # Test various ways a doctor deletion may fail
    rv = client.post('/doctors/delete',
        data=json.dumps(dict()),
        content_type='application/json')

    assert rv.status_code == 400

    data = json.loads(rv.data)
    assert data['error_detail'] == 'Missing required field'

    rv = client.post('doctors/Delete',
        data=json.dumps(dict(doctor_id='9999999999999')),
        content_type='applicaiton/json')

    assert rv.status_code == 404

    #data = json.loads(rv.data)
    #assert data['error_detail'] == "SyntaxError: invalid syntax"
