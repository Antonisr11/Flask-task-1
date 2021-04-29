from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from flask import Flask, request, jsonify, redirect, Response
import json
import uuid
import time
from datetime import date

# Connect to our local MongoDB
client = MongoClient('mongodb://localhost:27017/')

# Choose database
db = client['InfoSys']

# Choose collections
students = db['Students']
users = db['Users']

# Initiate Flask App
app = Flask(__name__)

users_sessions = {}


def create_session(username):
    user_uuid = str(uuid.uuid1())
    users_sessions[user_uuid] = (username, time.time())
    return user_uuid


def is_session_valid(user_uuid):
    return user_uuid in users_sessions


# ΕΡΩΤΗΜΑ 1: Δημιουργία χρήστη  OK_100
@app.route('/createUser', methods=['POST'])
def create_user():
    # Request JSON data
    data = None
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content", status=500, mimetype='application/json')
    if data == None:
        return Response("bad request", status=500, mimetype='application/json')
    if not "username" in data or not "password" in data:
        return Response("Information incomplete", status=500, mimetype="application/json")

    """
    Το συγκεκριμένο endpoint θα δέχεται στο body του request του χρήστη ένα json της μορφής: 

    {
        "username": "some username", 
        "password": "a very secure password"
    }

    * Θα πρέπει να εισαχθεί ένας νέος χρήστης στο σύστημα, ο οποίος θα εισάγεται στο collection Users (μέσω της μεταβλητής users). 
    * Η εισαγωγή του νέου χρήστη, θα γίνεται μόνο στη περίπτωση που δεν υπάρχει ήδη κάποιος χρήστης με το ίδιο username. 
    * Αν γίνει εισαγωγή του χρήστη στη ΒΔ, να επιστρέφεται μήνυμα με status code 200. 
    * Διαφορετικά, να επιστρέφεται μήνυμα λάθους, με status code 400.
    """

    # Έλεγχος δεδομένων username / password
    # Αν δεν υπάρχει user με το username που έχει δοθεί. 
    # Να συμπληρώσετε το if statement.
    if users.find({"username":data['username']}).count() == 0 :
        users.insert_one(data)
        # Μήνυμα επιτυχίας
        return Response(data['username'] + " was added to the MongoDB", mimetype='application/json', status=200)  # ΠΡΟΣΘΗΚΗ STATUS

    # Διαφορετικά, αν υπάρχει ήδη κάποιος χρήστης με αυτό το username.
    else:
    # Μήνυμα λάθους (Υπάρχει ήδη κάποιος χρήστης με αυτό το username)
        return Response("A user with the given username already exists", mimetype='application/json', status=400)  # ΠΡΟΣΘΗΚΗ STATUS


# ΕΡΩΤΗΜΑ 2: Login στο σύστημα  OK_100
@app.route('/login', methods=['POST'])
def login():
    # Request JSON data
    data = None
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content", status=500, mimetype='application/json')
    if data == None:
        return Response("bad request", status=500, mimetype='application/json')
    if not "username" in data or not "password" in data:
        return Response("Information incomplete", status=500, mimetype="application/json")

    """
        Να καλεστεί η συνάρτηση create_session() (!!! Η ΣΥΝΑΡΤΗΣΗ create_session() ΕΙΝΑΙ ΗΔΗ ΥΛΟΠΟΙΗΜΕΝΗ) 
        με παράμετρο το username μόνο στη περίπτωση που τα στοιχεία που έχουν δοθεί είναι σωστά, δηλαδή:
        * το data['username] είναι ίσο με το username που είναι στη ΒΔ (να γίνει αναζήτηση στο collection Users) ΚΑΙ
        * το data['password'] είναι ίσο με το password του συγκεκριμένου χρήστη.
        * Η συνάρτηση create_session() θα επιστρέφει ένα string το οποίο θα πρέπει να αναθέσετε σε μία μεταβλητή που θα ονομάζεται user_uuid.

        * Αν γίνει αυθεντικοποίηση του χρήστη, να επιστρέφεται μήνυμα με status code 200. 
        * Διαφορετικά, να επιστρέφεται μήνυμα λάθους με status code 400.
    """

    # Έλεγχος δεδομένων username / password
    # Αν η αυθεντικοποίηση είναι επιτυχής. 
    # Να συμπληρώσετε το if statement.
    if not (users.find({ "$and": [{"username":data['username']},{"password":data['password']}]}).count() == 0):
        res = {"uuid": create_session(data['username']), "username": data['username']}
        return Response(json.dumps(res), mimetype='application/json', status=200)  # ΠΡΟΣΘΗΚΗ STATUS

    # Διαφορετικά, αν η αυθεντικοποίηση είναι ανεπιτυχής.
    else:
    # Μήνυμα λάθους (Λάθος username ή password)
        return Response("Wrong username or password.", mimetype='application/json',status=400)  # ΠΡΟΣΘΗΚΗ STATUS


# ΕΡΩΤΗΜΑ 3: Επιστροφή φοιτητή βάσει email  OK_100
@app.route('/getStudent', methods=['GET'])
def get_student():
    # Request JSON data
    data = None
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content", status=500, mimetype='application/json')
    if data == None:
        return Response("bad request", status=500, mimetype='application/json')
    if not "email" in data:
        return Response("Information incomplete", status=500, mimetype="application/json")

    """
        Στα headers του request ο χρήστης θα πρέπει να περνάει το uuid το οποίο έχει λάβει κατά την είσοδό του στο σύστημα. 
            Π.Χ: uuid = request.headers.get['authorization']
        Για τον έλεγχο του uuid να καλεστεί η συνάρτηση is_session_valid() (!!! Η ΣΥΝΑΡΤΗΣΗ is_session_valid() ΕΙΝΑΙ ΗΔΗ ΥΛΟΠΟΙΗΜΕΝΗ) με παράμετρο το uuid. 
            * Αν η συνάρτηση επιστρέψει False ο χρήστης δεν έχει αυθεντικοποιηθεί. Σε αυτή τη περίπτωση να επιστρέφεται ανάλογο μήνυμα με response code 401. 
            * Αν η συνάρτηση επιστρέψει True, ο χρήστης έχει αυθεντικοποιηθεί. 

        Το συγκεκριμένο endpoint θα δέχεται σαν argument το email του φοιτητή και θα επιστρέφει τα δεδομένα του. 
        Να περάσετε τα δεδομένα του φοιτητή σε ένα dictionary που θα ονομάζεται student.

        Σε περίπτωση που δε βρεθεί κάποιος φοιτητής, να επιστρέφεται ανάλογο μήνυμα.
    """
    if is_session_valid(request.headers['authorization']):
        student = students.find_one({"email":data['email']})
        student['_id']=None

        if student is not None:
            # Η παρακάτω εντολή χρησιμοποιείται μόνο στη περίπτωση επιτυχούς αναζήτησης φοιτητών (δηλ. υπάρχει φοιτητής με αυτό το email).
            return Response(json.dumps(student), status=200, mimetype='application/json')
        else:
            return Response("There is no student with email: "+str(data['email']), status=400, mimetype='application/json')
    else:
        return Response("You haven't been authenticated",status=401 , mimetype='application/json')

# ΕΡΩΤΗΜΑ 4: Επιστροφή όλων των φοιτητών που είναι 30 ετών  ΟΚ_100
@app.route('/getStudents/thirties', methods=['GET'])
def get_students_thirty():
    """
        Στα headers του request ο χρήστης θα πρέπει να περνάει το uuid το οποίο έχει λάβει κατά την είσοδό του στο σύστημα. 
            Π.Χ: uuid = request.headers.get['authorization']
        Για τον έλεγχο του uuid να καλεστεί η συνάρτηση is_session_valid() (!!! Η ΣΥΝΑΡΤΗΣΗ is_session_valid() ΕΙΝΑΙ ΗΔΗ ΥΛΟΠΟΙΗΜΕΝΗ) με παράμετρο το uuid. 
            * Αν η συνάρτηση επιστρέψει False ο χρήστης δεν έχει αυθεντικοποιηθεί. Σε αυτή τη περίπτωση να επιστρέφεται ανάλογο μήνυμα με response code 401. 
            * Αν η συνάρτηση επιστρέψει True, ο χρήστης έχει αυθεντικοποιηθεί. 

        Το συγκεκριμένο endpoint θα πρέπει να επιστρέφει τη λίστα των φοιτητών οι οποίοι είναι 30 ετών.
        Να περάσετε τα δεδομένα των φοιτητών σε μία λίστα που θα ονομάζεται students.

        Σε περίπτωση που δε βρεθεί κάποιος φοιτητής, να επιστρέφεται ανάλογο μήνυμα και όχι κενή λίστα.
    """

    if is_session_valid(request.headers['authorization']):

        students_30 = students.find({"yearOfBirth":date.today().year-30})

        return_list = []
        for student in students_30:
            student['_id'] = None
            return_list.append(student)

        if students_30 is not None:
            # Η παρακάτω εντολή χρησιμοποιείται μόνο σε περίπτωση επιτυχούς αναζήτησης φοιτητών (δηλ. υπάρχουν φοιτητές που είναι 30 ετών).
            return Response(json.dumps(return_list), status=200, mimetype='application/json')
        else:
            return Response("There isn't any student at age of 30",status=400 , mimetype='application/json')
    else:
        return Response("You haven't been authenticated",status=401 , mimetype='application/json')

# ΕΡΩΤΗΜΑ 5: Επιστροφή όλων των φοιτητών που είναι τουλάχιστον 30 ετών  OK_100
@app.route('/getStudents/oldies', methods=['GET'])
def get_students_oldies():
    """
        Στα headers του request ο χρήστης θα πρέπει να περνάει και το uuid το οποίο έχει λάβει κατά την είσοδό του στο σύστημα. 
            Π.Χ: uuid = request.headers.get['authorization']
        Για τον έλεγχο του uuid να καλεστεί η συνάρτηση is_session_valid() (!!! Η ΣΥΝΑΡΤΗΣΗ is_session_valid() ΕΙΝΑΙ ΗΔΗ ΥΛΟΠΟΙΗΜΕΝΗ) με παράμετρο το uuid. 
            * Αν η συνάρτηση επιστρέψει False ο χρήστης δεν έχει αυθεντικοποιηθεί. Σε αυτή τη περίπτωση να επιστρέφεται ανάλογο μήνυμα με response code 401. 
            * Αν η συνάρτηση επιστρέψει True, ο χρήστης έχει αυθεντικοποιηθεί. 

        Το συγκεκριμένο endpoint θα πρέπει να επιστρέφει τη λίστα των φοιτητών οι οποίοι είναι 30 ετών και άνω.
        Να περάσετε τα δεδομένα των φοιτητών σε μία λίστα που θα ονομάζεται students.

        Σε περίπτωση που δε βρεθεί κάποιος φοιτητής, να επιστρέφεται ανάλογο μήνυμα και όχι κενή λίστα.
    """

    if is_session_valid(request.headers['authorization']):

        students_grandpas = students.find({"yearOfBirth": {"$lte": date.today().year - 30}})

        return_list = []
        for student in students_grandpas:
            student['_id'] = None
            return_list.append(student)

        if students_grandpas is not None:
            # Η παρακάτω εντολή χρησιμοποιείται μόνο σε περίπτωση επιτυχούς αναζήτησης φοιτητών (δηλ. υπάρχουν φοιτητές που είναι 30 ετών).
            return Response(json.dumps(return_list), status=200, mimetype='application/json')
        else:
            return Response("There isn't any student at age of 30", status=400, mimetype='application/json')

    else:
        return Response("You haven't been authenticated",status=401 , mimetype='application/json')


# ΕΡΩΤΗΜΑ 6: Επιστροφή φοιτητή που έχει δηλώσει κατοικία βάσει email  OK_100
@app.route('/getStudentAddress', methods=['GET'])
def get_student_address():
    # Request JSON data
    data = None
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content", status=500, mimetype='application/json')
    if data == None:
        return Response("bad request", status=500, mimetype='application/json')
    if not "email" in data:
        return Response("Information incomplete", status=500, mimetype="application/json")

    """
        Στα headers του request ο χρήστης θα πρέπει να περνάει και το uuid το οποίο έχει λάβει κατά την είσοδό του στο σύστημα. 
            Π.Χ: uuid = request.headers.get['authorization']
        Για τον έλεγχο του uuid να καλεστεί η συνάρτηση is_session_valid() (!!! Η ΣΥΝΑΡΤΗΣΗ is_session_valid() ΕΙΝΑΙ ΗΔΗ ΥΛΟΠΟΙΗΜΕΝΗ) με παράμετρο το uuid. 
            * Αν η συνάρτηση επιστρέψει False ο χρήστης δεν έχει αυθεντικοποιηθεί. Σε αυτή τη περίπτωση να επιστρέφεται ανάλογο μήνυμα με response code 401. 
            * Αν η συνάρτηση επιστρέψει True, ο χρήστης έχει αυθεντικοποιηθεί. 

        Το συγκεκριμένο endpoint θα δέχεται σαν argument το email του φοιτητή. 
        * Στη περίπτωση που ο φοιτητής έχει δηλωμένη τη κατοικία του, θα πρέπει να επιστρέφεται το όνομα του φοιτητή η διεύθυνσή του(street) και ο Ταχυδρομικός Κωδικός (postcode) της διεύθυνσης αυτής.
        * Στη περίπτωη που είτε ο φοιτητής δεν έχει δηλωμένη κατοικία, είτε δεν υπάρχει φοιτητής με αυτό το email στο σύστημα, να επιστρέφεται μήνυμα λάθους. 

        Αν υπάρχει όντως ο φοιτητής με δηλωμένη κατοικία, να περάσετε τα δεδομένα του σε ένα dictionary που θα ονομάζεται student.
        Το student{} να είναι της μορφής: 
        student = {"name": "Student's name", "street": "The street where the student lives", "postcode": 11111}
    """

    if is_session_valid(request.headers['authorization']):

        student = students.find_one({"email":data['email']})

        try:
            student = {"name":student['name'], "street":student['address'][0]['street'], "postcode":student['address'][0]['postcode']}
            # Η παρακάτω εντολή χρησιμοποιείται μόνο σε περίπτωση επιτυχούς αναζήτησης φοιτητών (δηλ. υπάρχουν φοιτητές που είναι 30 ετών).
            return Response(json.dumps(student), status=200, mimetype='application/json')
        except:
            return Response("Student with mail "+str(data['email'])+" has not address", status=400, mimetype='application/json')

    else:
        return Response("You haven't been authenticated",status=401 , mimetype='application/json')



# ΕΡΩΤΗΜΑ 7: Διαγραφή φοιτητή βάσει email  OK_100*
@app.route('/deleteStudent', methods=['GET'])
def delete_student():
    # Request JSON data
    data = None
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content", status=500, mimetype='application/json')
    if data == None:
        return Response("bad request", status=500, mimetype='application/json')
    if not "email" in data:
        return Response("Information incomplete", status=500, mimetype="application/json")

    """
        Στα headers του request ο χρήστης θα πρέπει να περνάει και το uuid το οποίο έχει λάβει κατά την είσοδό του στο σύστημα. 
            Π.Χ: uuid = request.headers.get['authorization']
        Για τον έλεγχο του uuid να καλεστεί η συνάρτηση is_session_valid() (!!! Η ΣΥΝΑΡΤΗΣΗ is_session_valid() ΕΙΝΑΙ ΗΔΗ ΥΛΟΠΟΙΗΜΕΝΗ) με παράμετρο το uuid. 
            * Αν η συνάρτηση επιστρέψει False ο χρήστης δεν έχει αυθεντικοποιηθεί. Σε αυτή τη περίπτωση να επιστρέφεται ανάλογο μήνυμα με response code 401. 
            * Αν η συνάρτηση επιστρέψει True, ο χρήστης έχει αυθεντικοποιηθεί. 

        Το συγκεκριμένο endpoint θα δέχεται σαν argument το email του φοιτητή. 
        * Στη περίπτωση που υπάρχει φοιτητής με αυτό το email, να διαγράφεται από τη ΒΔ. Να επιστρέφεται μήνυμα επιτυχούς διαγραφής του φοιτητή.
        * Διαφορετικά, να επιστρέφεται μήνυμα λάθους. 

        Και στις δύο περιπτώσεις, να δημιουργήσετε μία μεταβλήτη msg (String), η οποία θα περιλαμβάνει το αντίστοιχο μήνυμα.
        Αν βρεθεί ο φοιτητής και διαγραφεί, στο μήνυμα θα πρέπει να δηλώνεται και το όνομά του (πχ: msg = "Morton Fitzgerald was deleted.").
    """
    if is_session_valid(request.headers['authorization']):

        if students.find_one_and_delete({"email":data['email']}) is not None:
            status = 200
            msg = 'Deleted a student with email: ' + data['email']
        else:
            status=400
            msg = "There is no student with email " + str(data['email']) + " therefore there was no deletion."

        return Response(msg, status=status ,mimetype='application/json')

    else:
        return Response("You haven't been authenticated",status=401 , mimetype='application/json')


# ΕΡΩΤΗΜΑ 8: Εισαγωγή μαθημάτων σε φοιτητή βάσει email  OK_100
@app.route('/addCourses', methods=['GET'])
def add_courses():
    # Request JSON data
    data = None
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content", status=500, mimetype='application/json')
    if data == None:
        return Response("bad request", status=500, mimetype='application/json')
    if not "email" in data or not "courses" in data:
        return Response("Information incomplete", status=500, mimetype="application/json")

    """
        Στα headers του request ο χρήστης θα πρέπει να περνάει και το uuid το οποίο έχει λάβει κατά την είσοδό του στο σύστημα. 
            Π.Χ: uuid = request.headers.get['authorization']
        Για τον έλεγχο του uuid να καλεστεί η συνάρτηση is_session_valid() (!!! Η ΣΥΝΑΡΤΗΣΗ is_session_valid() ΕΙΝΑΙ ΗΔΗ ΥΛΟΠΟΙΗΜΕΝΗ) με παράμετρο το uuid. 
            * Αν η συνάρτηση επιστρέψει False ο χρήστης δεν έχει αυθεντικοποιηθεί. Σε αυτή τη περίπτωση να επιστρέφεται ανάλογο μήνυμα με response code 401. 
            * Αν η συνάρτηση επιστρέψει True, ο χρήστης έχει αυθεντικοποιηθεί. 

        Το συγκεκριμένο endpoint θα δέχεται σαν argument το email του φοιτητή. Στο body του request θα πρέπει δίνεται ένα json της παρακάτω μορφής:

        {
            email: "an email",
            courses: [
                {'course 1': 10, 
                {'course 2': 3 }, 
                {'course 3': 8},
                ...
            ]
        } 

        Η λίστα courses έχει μία σειρά από dictionary για τα οποία τα key αντιστοιχούν σε τίτλο μαθημάτων και το value στο βαθμό που έχει λάβει ο φοιτητής σε αυτό το μάθημα.
        * Στη περίπτωση που υπάρχει φοιτητής με αυτό το email, θα πρέπει να γίνει εισαγωγή των μαθημάτων και των βαθμών τους, σε ένα νέο key του document του φοιτητή που θα ονομάζεται courses. 
        * Το νέο αυτό key θα πρέπει να είναι μία λίστα από dictionary.
        * Αν δε βρεθεί φοιτητής με αυτό το email να επιστρέφεται μήνυμα λάθους. 
    """

    if is_session_valid(request.headers['authorization']):
        if students.find_one_and_update({"email":data['email']},{"$set" : {"courses": data['courses'] }}) is not None:
            return Response('Courses on this student added successfully!', status = 200, mimetype='application/json')
        else:
            return Response("There is no student with email " + str(data['email']) + " therefore there was no deletion.",status=400, mimetype='application/json')

    else:
        return Response("You haven't been authenticated",status=401 , mimetype='application/json')


# ΕΡΩΤΗΜΑ 9: Επιστροφή περασμένων μαθημάτων φοιτητή βάσει email
@app.route('/getPassedCourses', methods=['GET'])
def get_courses():
    # Request JSON data
    data = None
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content", status=500, mimetype='application/json')
    if data == None:
        return Response("bad request", status=500, mimetype='application/json')
    if not "email" in data:
        return Response("Information incomplete", status=500, mimetype="application/json")

    """
        Στα headers του request ο χρήστης θα πρέπει να περνάει και το uuid το οποίο έχει λάβει κατά την είσοδό του στο σύστημα. 
            Π.Χ: uuid = request.headers.get['authorization']
        Για τον έλεγχο του uuid να καλεστεί η συνάρτηση is_session_valid() (!!! Η ΣΥΝΑΡΤΗΣΗ is_session_valid() ΕΙΝΑΙ ΗΔΗ ΥΛΟΠΟΙΗΜΕΝΗ) με παράμετρο το uuid. 
            * Αν η συνάρτηση επιστρέψει False ο χρήστης δεν έχει αυθεντικοποιηθεί. Σε αυτή τη περίπτωση να επιστρέφεται ανάλογο μήνυμα με response code 401. 
            * Αν η συνάρτηση επιστρέψει True, ο χρήστης έχει αυθεντικοποιηθεί. 

        Το συγκεκριμένο endpoint θα δέχεται σαν argument το email του φοιτητή.
        * Στη περίπτωση που ο φοιτητής έχει βαθμολογία σε κάποια μαθήματα, θα πρέπει να επιστρέφεται το όνομά του (name) καθώς και τα μαθήματα που έχει πέρασει.
        * Στη περίπτωη που είτε ο φοιτητής δεν περάσει κάποιο μάθημα, είτε δεν υπάρχει φοιτητής με αυτό το email στο σύστημα, να επιστρέφεται μήνυμα λάθους.

        Αν υπάρχει όντως ο φοιτητής με βαθμολογίες σε κάποια μαθήματα, να περάσετε τα δεδομένα του σε ένα dictionary που θα ονομάζεται student.
        Το dictionary student θα πρέπει να είναι της μορφής: student = {"course name 1": X1, "course name 2": X2, ...}, όπου X1, X2, ... οι βαθμολογίες (integer) των μαθημάτων στα αντίστοιχα μαθήματα.
    """

    if is_session_valid(request.headers['authorization']):

        student = students.find_one({ "$and": [{"courses": { "$exists": "true", "$ne": "null" }},{"email":data['email']}]})

        if student is not None:

            has_passed_at_least_one = False
            student_build = "{ \"name\": \""+str(student['name'])+"\""
            for course_name, course_grade in student['courses'].items():
                if int(course_grade) >=5:
                    student_build += ", \""+course_name+"\": "+str(course_grade)
                    has_passed_at_least_one = True
            student_build += "}"

            student = json.loads(student_build)
            if has_passed_at_least_one:
                # Η παρακάτω εντολή χρησιμοποιείται μόνο σε περίπτωση επιτυχούς αναζήτησης φοιτητή (υπάρχει ο φοιτητής και έχει βαθμολογίες στο όνομά του).
                return Response(json.dumps(student), status=200, mimetype='application/json')
            else:
                return Response("Student with name "+str(student['name'])+" hasn't any passed course", status=201, mimetype='application/json')

        else:
            return Response("There isn't any student with email "+str(data['email'])+" or courses are not inputted yet", status=400, mimetype='application/json')
    else:
        return Response("You haven't been authenticated",status=401 , mimetype='application/json')

# @app.route('/test/<int:where>')
# def test(where):
#     import requests
#     def test3():
#         return requests.post('http://127.0.0.1:5000/login', data="{\"username\": \"ant\", \"password\": \"0\" }").text[10:-21]
#     def clear_all():
#         global users_sessions
#         users.drop()
#         users_sessions = {}
#         return Response("Cleared users and users_sessions!")
#
#     print("Welcome to test",where)
#
#     if where == 1:
#         return Response(requests.post('http://127.0.0.1:5000/createUser', data="{\"username\": \"ant\", \"password\": \"0\" }"))
#     elif where == 2:
#         return Response(requests.post('http://127.0.0.1:5000/login', data="{\"username\": \"ant\", \"password\": \"0\" }"))
#     elif where == 3:
#         return Response(requests.get('http://127.0.0.1:5000/getStudent', data="{\"email\":\"everettrich@ontagene.com\"}",
#                      headers=json.loads("{\"authorization\":\"" + test3() + "\"}")))
#     elif where == 4:
#         return Response(requests.get('http://127.0.0.1:5000/getStudents/thirties', headers=json.loads("{\"authorization\":\"" + test3() + "\"}")))
#     elif where == 5:
#         return Response(requests.get('http://127.0.0.1:5000/getStudents/oldies', headers=json.loads("{\"authorization\":\"" + test3() + "\"}")))
#     elif where == 6:
#         return Response(requests.get('http://127.0.0.1:5000/getStudentAddress', data="{\"email\":\"everettrich@ontagene.com\"}", headers=json.loads("{\"authorization\":\"" + test3() + "\"}")))
#     elif where == 7:
#         return Response(requests.get('http://127.0.0.1:5000/deleteStudent', data="{\"email\":\"allisonturner@ontagene.com\"}", headers=json.loads("{\"authorization\":\"" + test3() + "\"}")))
#     elif where == 8:
#         temp = "{ \"mathima_1\": 0, \"mathima_2\": 2, \"mathima_3\":4 }"
#         return Response(
#             requests.get('http://127.0.0.1:5000/addCourses', data="{\"email\":\"everettrich@ontagene.com\",\"courses\":"+temp+"}",
#                          headers=json.loads("{\"authorization\":\"" + test3() + "\"}")))
#     elif where == 9:
#         return Response(
#             requests.get('http://127.0.0.1:5000/getPassedCourses', data="{\"email\":\"everettrich@ontagene.com\"}",
#                          headers=json.loads("{\"authorization\":\"" + test3() + "\"}")))
#     elif where == 2873:
#         return clear_all()
# 
#     return Response("Emmm ok..?")


# Εκτέλεση flask service σε debug mode, στην port 5000.
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)