import json

def test_get_all_locations_for_doctor_id(client):
    # Test getting locations for one doctor(by ID)
    rv = client.get('/doctors/0/locations')
    assert rv.status_code == 200

    # Can't guarantee order, so test that we get the expected count and fields seem to make sense
    data = json.loads(rv.data)
    assert len(data) == 2
    for field in ['id', 'address']:
        assert field in data[0]


def test_add_location(client):
    # Test creating a new location, successfully

    rv = client.post('/locations/add',
        data=json.dumps(dict(address='32 Wallaby Lane')),
        content_type='application/json')

    assert rv.status_code == 200

    data = json.loads(rv.data)
    assert data['Added Location_ID:'] == 2


def test_add_invalid_location(client):
    # Test various ways adding a location may fail
    rv = client.post('/locations/add',
        data=json.dumps(dict( )),
        content_type='application/json')

    assert rv.status_code == 400

    data = json.loads(rv.data)
    assert data['error_detail'] == 'Missing required field'


def test_assign_location(client):
    # Test adding an additional location assignment to a doctor, successfully
    rv = client.post('/doctors/locations/assign',
        data=json.dumps(dict(location_id='1', doctor_id='0')),
        content_type='application/json')

    assert rv.status_code == 200

    data = json.loads(rv.data)
    assert data['doctor_location_id: '] == 3


def test_assign_invalid_location(client):
    # Test various ways adding a location may fail
    rv = client.post('/doctors/locations/assign',
        data=json.dumps(dict( )),
        content_type='application/json')

    assert rv.status_code == 400

    data = json.loads(rv.data)
    assert data['error_detail'] == 'Missing required field'

    rv = client.post('/doctors/locations/assign',
        data=json.dumps(dict(doctor_id='5')),
        content_type='application/json')

    assert rv.status_code == 400

    data = json.loads(rv.data)
    assert data['error_detail'] == 'Missing required field'

    rv = client.post('/doctors/locations/assign',
        data=json.dumps(dict(location_id='88')),
        content_type='application/json')

    assert rv.status_code == 400
