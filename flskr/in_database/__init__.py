import os
import time
from datetime import date, datetime 

from flask import Flask, jsonify, request
from in_database import db


# Program & structure influenced heavily by the Flask tutorial
# http://flask.pocoo.org/docs/1.0/tutorial/database/
def create_app(test_config=None):
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        # a default secret that should be overridden by instance config
        SECRET_KEY='dev',
        # store the database in the instance folder
        DATABASE=os.path.join(app.instance_path, 'doctors.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.update(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Register the database commands
    db.init_app(app)


    # Gets all doctors
    @app.route('/doctors', methods=['GET'])
    def list_doctors():
        """
        Get all doctors

        :return: List of full doctor rows
        """
        try:
            cursor = db.get_db().cursor()

            result = cursor.execute(
                'SELECT id, first_name, last_name '
                'FROM doctors'
            ).fetchall()

            # See https://medium.com/@PyGuyCharles/python-sql-to-json-and-beyond-3e3a36d32853
            doctors = [dict(zip([key[0] for key in cursor.description], row)) for row in result]

            cursor.close()
        except Exception as e:
            return e
        return jsonify(doctors), 200

    
    # Updates doctor names by ID
    @app.route('/doctors/update', methods=['POST'])
    def doc_update():
        '''
        updates doctor information by doctor ID

        returns "Updated from (old) to (new)"
        '''
        try:
            cursor = db.get_db().cursor()

            req_data = request.get_json()
            
            try:
                doctor_id = req_data['doctor_id']
                first_name = req_data['first_name']
                last_name = req_data['last_name']
            except KeyError as e:
                return jsonify({'error_detail': 'Missing required field(s)'}), 400

            cursor.execute(
                "UPDATE doctors SET "
                "first_name = ?, "
                "last_name = ? "
                "WHERE id == ?",
                (first_name, last_name, doctor_id)
            )
            
            db.get_db().commit()

            update_result = cursor.execute(
                "SELECT * FROM doctors "
                "WHERE id = ?",
                (doctor_id, )
            ).fetchone() 

            doctor_update = dict(zip([key[0] for key in cursor.description], update_result))

            cursor.close() 

            return jsonify(doctor_update)      
        except Exception as e:
            return jsonify({'error_detail': str(e)}), 404
    

    # Gets Doctor info by ID
    @app.route('/doctors/<int:doctor_id>', methods=['GET'])
    def list_doctor(doctor_id):
        """
        Get one doctor by doc_id

        :param doctor_id: The id of the doctor
        :return: Full doctor row
        """
        try:
            cursor = db.get_db().cursor()

            result = cursor.execute(
                'SELECT id, first_name, last_name '
                'FROM doctors '
                'WHERE id = ?',
                (doctor_id, )
            ).fetchone()

            if result is None:
                return jsonify({'error_detail': 'Doctor not found'}), 404

            # See https://medium.com/@PyGuyCharles/python-sql-to-json-and-beyond-3e3a36d32853
            doctor = dict(zip([key[0] for key in cursor.description], result))

            cursor.close()
        except Exception as e:
            return e
        return jsonify(doctor), 200


    # Deletes Doctors
    @app.route('/doctors/delete', methods=['POST'])
    def delete_doctors():
        '''
        Deletes Doctor from  the DB...

        Should probably be handled as a flag instead(?)

        To prevent any potential abuse from outside forces?
        '''
        try:

            req_data = request.get_json()
            
            try:
                doctor_id = req_data['doctor_id']
            except KeyError as e:
                return jsonify({'error_detail': 'Missing required field'}), 400

            cursor = db.get_db().cursor()

            cursor.execute(
                "DELETE FROM doctors WHERE id == ?",
                (doctor_id, )
            )
            
            db.get_db().commit()
            cursor.close()
        
        except Exception as e:
            return jsonify({'error_detail': str(e)}), 404
        return jsonify({"Removed doctor with ID: ":doctor_id}), 200


    # Creates and adds a Doctor for use in the database
    # Note: Must set the content type to JSON. Use something like:
    # curl -X POST -H "Content-Type: application/json" --data '{"first_name": "Joe", "last_name": "Smith"}' http://localhost:5000/doctors
    @app.route('/doctors', methods=['POST'])
    def add_doctor():
        """
        Create a doctor

        :param first_name: The doctor's first name
        :param last_name: The doctor's last name

        :return: The id of the newly created doctor
        """
        try:
            req_data = request.get_json()

            try:
                first_name = req_data['first_name']
                last_name = req_data['last_name']
            except KeyError:
                return jsonify({'error_detail': 'Missing required field'}), 400

            cursor = db.get_db().cursor()

            cursor.execute(
                'INSERT INTO doctors (first_name, last_name) '
                'VALUES (?, ?)',
                (first_name, last_name)
            )

            doctor_id = cursor.lastrowid

            db.get_db().commit()
            cursor.close()
        except Exception as e:
            return jsonify({'error_detail': e}), 404
        return jsonify({'id': doctor_id}), 200


    # Returns the locations a singular doctor works at.
    @app.route('/doctors/<int:doctor_id>/locations', methods=['GET'])
    def list_doctor_locations(doctor_id):
        """
        Get the locations for a single doctor

        :param doctor_id: The id of the doctor
        :return: List of full location rows
        """
        try:
            cursor = db.get_db().cursor()

            result = cursor.execute(
                'SELECT l.id, l.address '
                'FROM doctor_locations dl '
                'INNER JOIN locations l ON dl.location_id = l.id '
                'WHERE dl.doctor_id = ?',
                (doctor_id,)
            ).fetchall()

            # See https://medium.com/@PyGuyCharles/python-sql-to-json-and-beyond-3e3a36d32853
            locations = [dict(zip([key[0] for key in cursor.description], row)) for row in result]

            cursor.close()

        except Exception as e:
            return jsonify({'error_detail': str(e)}), 404

        return jsonify(locations), 200


    # Adds location to total list; (new building) NOT COMPLETE
    @app.route('/locations/add', methods=['POST'])
    def add_locations():
        
        try:
            cursor = db.get_db().cursor()

            req_data = request.get_json()

            try:
                address = req_data['address']
            except KeyError:
                return jsonify({'error_detail': 'Missing required field'}), 400
        
            cursor.execute(
                "INSERT INTO locations(address) VALUES (?)",
                (address, ) 
            )
            db.get_db().commit()

            loc_id = cursor.lastrowid
            
            cursor.close()
        except Exception   as e:
            return jsonify(str(e)), 404
        return jsonify ({"Added Location_ID:": loc_id}), 200
        
    
    # Assign facility to doctors
    @app.route('/doctors/locations/assign', methods=['POST'])
    def assign_locations():
        try:
            cursor = db.get_db().cursor()

            req_data = request.get_json()

            try:
                loc_id = req_data['location_id']
                doc_id = req_data['doctor_id']
            except KeyError:
                return jsonify({'error_detail': 'Missing required field'}), 400
        
            cursor.execute(
                "INSERT INTO doctor_locations(doctor_id, location_id) VALUES (?, ?)",
                (doc_id, loc_id) 
            )

            db.get_db().commit()
            
            doctor_location_id = cursor.lastrowid

            cursor.close()

        except Exception as e:
            return jsonify(str(e)), 404
        return jsonify({"doctor_location_id: ": doctor_location_id}),200


    # Enters working hours of the doctor
    @app.route('/doctor/hours/set', methods=["POST"])
    def set_hours():
        try:
            cursor = db.get_db().cursor()
            
            req_data = request.get_json()

            try:
                doc_id = req_data['doctor_id']
                shift_start = req_data['shift_start']
                shift_end = req_data['shift_end']
            except KeyError:
                return jsonify({'error_detail': 'Missing required field'}), 400
        
            cursor.execute(
                "INSERT INTO doctor_hours(doctor_id, shift_start, shift_end) VALUES (?, ?, ?)",
                (doc_id, shift_start, shift_end) 
            )

            db.get_db().commit()

            doctor_hours_id = cursor.lastrowid

            cursor.close()

        except Exception as e:
            return jsonify({"error detail:": e}), 404
        return jsonify ({"shift start / end ID: ":doctor_hours_id}), 200
       
    
    # Updates the is_canceled flag for appointments
    @app.route('/doctors/appointment/cancel', methods=['POST'])
    def cancel_appointment():
        '''
        Cancels appointments by Appointment ID.

        Each Appointment ID is unique to each appointment, so 
        each date / time code and location are bound to the unique ID.

        returns appointment cancelled (and appointment ID of said appointment)

        Also makes the Appointment available for other requests.

        ALternatively could be handled by a delete request.
        '''
        try:
            cursor = db.get_db().cursor()

            req_data = request.get_json()

            appointment_id = req_data['appointment_id']

            cursor.execute(
                "UPDATE appointments SET is_canceled = 1 WHERE id == ?",
                (appointment_id, )
            )
            
            db.get_db().commit()
            cursor.close()
        
        except Exception as e:
            return jsonify({'error_detail': str(e)}), 404
        return jsonify({"Canceled Appointment_id":appointment_id}), 200


    # Schedules appointments
    @app.route('/doctors/make_appointment/', methods=['POST'])
    def schedule_appointment():
        '''
        Schedules the appointment

        checks if the doctor has working hours.

        Prevents overlapping appointments +/- 15 minutes(14:59, to be exact...)
            Should update / add field for appointment type; provide a lock on +/- time where the 

        Returns: 
        Appointment ID
        or
        Appointment Taken
        '''
        cursor = db.get_db().cursor()

        #Gets schedule Day / Date
        def get_day(apmnt_time):
            try:
                string_date =  datetime.fromtimestamp(apmnt_time).strftime('%m  %d %Y')
                my_date = datetime.strptime(string_date, '%m %d %Y')
                tstamp = datetime.timestamp(my_date)

            except Exception as e:
                return str(e)
            return int(tstamp)

        #Check doctor availability (is the doctor in the office / have working hours)
        def doc_avail(arg1):
            try:    
                result = cursor.execute(
                    "SELECT doctor_id, shift_start, shift_end FROM doctor_hours "
                    "WHERE doctor_id == ?",
                    (arg1[0], )
                ).fetchall()

                doctor_availability = [dict(zip([key[0] for key in cursor.description], row)) for row in result]
                
                avail_dict_list = list(filter(lambda start_time: start_time['shift_start'] <= arg1[2], doctor_availability))

                shift_end_time = avail_dict_list[0].get("shift_end", False)

                if (shift_end_time <= arg1[2]):
                    return 1
                elif (shift_end_time >= arg1[2]):
                    return 0
            except Exception as e:
                return str(e)
    
        #Checks if there is an appointment scheduled in the next +- 15 minutes (14:59, technically)
        def check_apmnt(arg1):
            try:

                '''
                checks for an appointment in the specified range
                +/- 899 seconds, or 14:59 minutes:seconds.

                :return 0: if there are no scheduled appointemnts

                :return 1: if there is a scheudled appointment

                :return 2: on error.
                '''
                sched_time = arg1[2]
                offset = 899 
                
                '''
                Determines block of time to block off
                '''
                time_block_add = sched_time + offset

                time_block_sub = sched_time - offset

                time_block_check = cursor.execute(
                    'SELECT id FROM appointments '
                    'WHERE doctor_id == ? '
                    'AND apmnt_time BETWEEN ? AND ?',
                    (arg1[0], time_block_sub, time_block_add)
                ).fetchone()

                if time_block_check is None:
                    return 0
                else:
                    return 1
            except Exception as e:
                return str(e)
        
        #Writes the Data
        def write_data(apmnt_check, arg2, doc_check, day_stamp):
            '''
            wites the data, or returns "Doctor Unavailable; please select different time."

            '''
            try:
                if (apmnt_check != 0 | doc_check != 0):
                    return "Doctor Unavailable; please select a different time."
                elif (apmnt_check == 0 & doc_check == 0):
                    cursor.execute(
                        'INSERT INTO appointments (day_stamp, doctor_id, location_id, ' 
                        'apmnt_time, is_canceled)'
                        'VALUES (?, ?, ?, ?, 0)',
                        (day_stamp, arg2[0], arg2[1], arg2[2])
                    )
            
                    appointment_id = cursor.lastrowid

                    db.get_db().commit()
                    cursor.close()
                    
                    return appointment_id      
                else:
                    return "Please select a different Time."
            except Exception as e:
                return str(e)
        
        try:
            
            req_data = request.get_json()

            doc_id = req_data['doctor_id']
            loc_id = req_data['location_id']
            apmnt_time = int(req_data['apmnt_time'])

            apmnt_tup = (doc_id, loc_id, apmnt_time)
            
            apmnt_check = check_apmnt(apmnt_tup)
            
            doc_check = doc_avail(apmnt_tup)

            apmnt_date = get_day(apmnt_time)

            appointment_id = write_data(apmnt_check, apmnt_tup, doc_check, apmnt_date)
        
        except Exception as e:
            return jsonify({'error_detail': str(e)}), 404

        return jsonify({"Appointment ID: ":appointment_id}), 200


    # Gets the weekly schedule by Doctor ID.
    @app.route('/doctors/weekly_schedule/<int:doctor_id>', methods=['GET'])
    def get_doctor_sched(doctor_id):
        """
        Get all appointments for each doctor by Doctor ID for next week.
        
        :return: Full appointments row for the next week.
        """ 
        cursor = db.get_db().cursor()
        def get_day():
            try:
                string_date =  datetime.today().strftime('%m  %d %Y')
                my_date = datetime.strptime(string_date, '%m %d %Y')
                tstamp = datetime.timestamp(my_date)

            except Exception as e:
                return str(e)
            return int(tstamp)

        current_day = get_day()
        one_week = current_day + 604800
        
                                            
        def get_doc_work_hrs(doctor_id):
            try:
                doc_work_hours = cursor.execute(                    
                    'SELECT dhrs.day_stamp, d.first_name, d.last_name, dhrs.shift_start, dhrs.shift_end '
                    'FROM doctor_hours dhrs '
                    'INNER JOIN doctors d ON dhrs.doctor_id = d.id '
                    'WHERE dhrs.doctor_id = ? '
                    'AND dhrs.day_stamp BETWEEN ? AND ?',
                    (doctor_id, current_day, one_week)
                    ).fetchall()
                
                dhrs = [dict(zip([key[0] for key in cursor.description], row)) for row in doc_work_hours]

                if doc_work_hours is None:
                    return jsonify({'error_detail': 'not found'}), 404
            
            except Exception as e:
                return str(e)
            
            return dhrs
    
        def get_doctors_appointments(doctor_id):
            try:
                week_appointments = cursor.execute(
                    'SELECT apmnt.day_stamp, d.first_name, d.last_name, l.address, apmnt.apmnt_time '
                    'FROM appointments apmnt '
                    'INNER JOIN locations l ON apmnt.location_id = l.id '
                    'INNER JOIN doctors d ON apmnt.doctor_id = d.id '
                    'WHERE apmnt.doctor_id = ? '
                    'AND apmnt.day_stamp BETWEEN ? AND ?',
                    (doctor_id, current_day, one_week)
                ).fetchall()

                doctors_appointments = [dict(zip([key[0] for key in cursor.description], row)) for row in week_appointments]

                if week_appointments is None:
                    return jsonify({'error_detail': 'not found'}), 404

            except Exception as e:
                return e

            return doctors_appointments

        def combine_data(arg1, arg2):
            try:
                combined_list = [*arg1, *arg2]

            except Exception as e:
                return str(e)
            
            return combined_list
        
        try:
            doc_hours = get_doc_work_hrs(doctor_id)
            doc_apmnts = get_doctors_appointments(doctor_id)
            result = combine_data(doc_hours, doc_apmnts)
            cursor.close()

        except Exception as e:
            return jsonify({"error detail:": str(e)}), 404
        
        return jsonify(result), 200


    # Gets ALL doctor appointments for ea. doctor by Doctor ID # need to make one dict where the 
    @app.route('/doctors/appointment/<int:doctor_id>', methods=['GET']) 
    def get_doctor_appointments(doctor_id):
        """
        Get all appointments for each doctor by Doctor ID.
        
        :return: Full appointments row for the doctor.
        """ 
        cursor = db.get_db().cursor()
        
        result = cursor.execute(
            'SELECT d.first_name, d.last_name, l.address, apmnt.apmnt_time '
            'FROM appointments apmnt '
            'INNER JOIN locations l ON apmnt.location_id = l.id '
            'INNER JOIN doctors d ON apmnt.doctor_id = d.id '
            'WHERE apmnt.doctor_id = ?',
            (doctor_id, )
        ).fetchall()

        if result is None:
            return jsonify({'error_detail': 'not found'}), 404

        appointments = [dict(zip([key[0] for key in cursor.description], row)) for row in result]

        cursor.close()

        return jsonify(appointments), 200


    return app
