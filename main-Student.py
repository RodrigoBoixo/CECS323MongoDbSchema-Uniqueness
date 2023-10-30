import pymongo
from pymongo import MongoClient
from pprint import pprint
import getpass
from menu_definitions import menu_main
from menu_definitions import add_menu
from menu_definitions import delete_menu
from menu_definitions import list_menu


def add_department(db):
    running = True
    while running:
        try:
            # Get user input
            name = input("Enter the department name (min 10 characters, max 50 characters): ")
            abbreviation = input("Enter the department abbreviation (max 6 characters): ")
            chair_name = input("Enter the chair name (max 80 characters): ")
            building = input("Enter the building (max 10 characters): ")
            office = int(input("Enter the office number: "))
            description = input("Enter the department description (max 80 characters): ")

            # Create department document
            department = {
                "_id": name,
                "abbreviation": abbreviation,
                "chair_name": chair_name,
                "building": building,
                "office": office,
                "description": description
            }

            # Insert department into the collection (this will raise an exception if constraints are violated)
            db.departments.insert_one(department)
            #running = False  # Exit the loop once the department is added successfully

        except pymongo.errors.DuplicateKeyError as e:
            print("Error:", e.details['errmsg'])
            print("Please re-enter the department details.")
            continue
        except pymongo.errors.WriteError as e:
            print("Error:", e.details['errmsg'])
            print("Please re-enter the department details.")
            continue
        except Exception as e:
            print("Error:", e)
            print("Please re-enter the department details.")
            continue

        #collection = db["departments"]

        # If all checks pass, insert the department into the collection
        #results = collection.insert_one(department)
        #give confirmation to user that the department was added
        print(f"Department {department['_id']} added successfully.")
        running = False

def select_department(db):
    #implemented as seen from student select
    collection = db["departments"]
    found = False
    name = ''
    while not found:
        name = input("Enter the name of the department: ")
        name_count: int = collection.count_documents({"_id": name})
        found = name_count == 1
        if not found:
            print("No department found by that name.  Try again.")
    found_department = collection.find_one({"_id": name})
    return found_department


def delete_department(db):
    #implemented as seen from student delete

    department = select_department(db)

    # Delete the department from the database
    departments = db["departments"]
    deleted = departments.delete_one({"_id": department["_id"]})
    print(f"We just deleted: {deleted.deleted_count} department.")


def list_department(db):
    #implemented as seen from student list
    # Fetch and display all departments sorted by name
    departments = db["departments"].find({}).sort([("_id", pymongo.ASCENDING)])
    for department in departments:
        pprint(department)


def add(db):
    """
    Present the add menu and execute the user's selection.
    :param db:  The connection to the current database.
    :return:    None
    """
    add_action: str = ''
    while add_action != add_menu.last_action():
        add_action = add_menu.menu_prompt()
        exec(add_action)


def delete(db):
    """
    Present the delete menu and execute the user's selection.
    :param db:  The connection to the current database.
    :return:    None
    """
    delete_action: str = ''
    while delete_action != delete_menu.last_action():
        delete_action = delete_menu.menu_prompt()
        exec(delete_action)


def list_objects(db):
    """
    Present the list menu and execute the user's selection.
    :param db:  The connection to the current database.
    :return:    None
    """
    list_action: str = ''
    while list_action != list_menu.last_action():
        list_action = list_menu.menu_prompt()
        exec(list_action)


def add_student(db):
    """
    Add a new student, making sure that we don't put in any duplicates,
    based on all the candidate keys (AKA unique indexes) on the
    students collection.  Theoretically, we could query MongoDB to find
    the uniqueness constraints in place, and use that information to
    dynamically decide what searches we need to do to make sure that
    we don't violate any of the uniqueness constraints.  Extra credit anyone?
    :param collection:  The pointer to the students collection.
    :return:            None
    """
    # Create a "pointer" to the students collection within the db database.
    collection = db["students"]
    unique_name: bool = False
    unique_email: bool = False
    lastName: str = ''
    firstName: str = ''
    email: str = ''
    while not unique_name or not unique_email:
        lastName = input("Student last name--> ")
        firstName = input("Student first name--> ")
        email = input("Student e-mail address--> ")
        name_count: int = collection.count_documents({"last_name": lastName, "first_name": firstName})
        unique_name = name_count == 0
        if not unique_name:
            print("We already have a student by that name.  Try again.")
        if unique_name:
            email_count = collection.count_documents({"e_mail": email})
            unique_email = email_count == 0
            if not unique_email:
                print("We already have a student with that e-mail address.  Try again.")
    # Build a new students document preparatory to storing it
    student = {
        "last_name": lastName,
        "first_name": firstName,
        "e_mail": email
    }
    results = collection.insert_one(student)


def select_student(db):
    """
    Select a student by the combination of the last and first.
    :param db:      The connection to the database.
    :return:        The selected student as a dict.  This is not the same as it was
                    in SQLAlchemy, it is just a copy of the Student document from
                    the database.
    """
    # Create a connection to the students collection from this database
    collection = db["students"]
    found: bool = False
    lastName: str = ''
    firstName: str = ''
    while not found:
        lastName = input("Student's last name--> ")
        firstName = input("Student's first name--> ")
        name_count: int = collection.count_documents({"last_name": lastName, "first_name": firstName})
        found = name_count == 1
        if not found:
            print("No student found by that name.  Try again.")
    found_student = collection.find_one({"last_name": lastName, "first_name": firstName})
    return found_student


def delete_student(db):
    """
    Delete a student from the database.
    :param db:  The current database connection.
    :return:    None
    """
    # student isn't a Student object (we have no such thing in this application)
    # rather it's a dict with all the content of the selected student, including
    # the MongoDB-supplied _id column which is a built-in surrogate.
    student = select_student(db)
    # Create a "pointer" to the students collection within the db database.
    students = db["students"]
    # student["_id"] returns the _id value from the selected student document.
    deleted = students.delete_one({"_id": student["_id"]})
    # The deleted variable is a document that tells us, among other things, how
    # many documents we deleted.
    print(f"We just deleted: {deleted.deleted_count} students.")


def list_student(db):
    """
    List all of the students, sorted by last name first, then the first name.
    :param db:  The current connection to the MongoDB database.
    :return:    None
    """
    # No real point in creating a pointer to the collection, I'm only using it
    # once in here.  The {} inside the find simply tells the find that I have
    # no criteria.  Essentially this is analogous to a SQL find * from students.
    # Each tuple in the sort specification has the name of the field, followed
    # by the specification of ascending versus descending.
    students = db["students"].find({}).sort([("last_name", pymongo.ASCENDING),
                                             ("first_name", pymongo.ASCENDING)])
    # pretty print is good enough for this work.  It doesn't have to win a beauty contest.
    for student in students:
        pprint(student)


if __name__ == '__main__':
    # password: str = getpass.getpass('Mongo DB password -->')
    password = "Carm3n1ta"
    username: str = input('Database username [CECS-323-Spring-2023-user] -->') or "rboixo"
    project: str = input('Mongo project name [cecs-323-spring-2023] -->') or "atlascluster"
    hash_name: str = input('7-character database hash [puxnikb] -->') or "wxir5tb"
    cluster = f"mongodb+srv://{username}:{password}@{project}.{hash_name}.mongodb.net/?retryWrites=true&w=majority&authSource=admin" #&authSource=admin
    print(f"Cluster: mongodb+srv://{username}:********@{project}.{hash_name}.mongodb.net/?retryWrites=true&w=majority&authSource=admin") #&authSource=admin
    client = MongoClient(cluster)
    # As a test that the connection worked, print out the database names.
    print(client.list_database_names())
    # db will be the way that we refer to the database from here on out.
    db = client["Demonstration"]
    # Print off the collections that we have available to us, again more of a test than anything.
    print(db.list_collection_names())
    # student is our students collection within this database.
    # Merely referencing this collection will create it, although it won't show up in Atlas until
    # we insert our first document into this collection.
    students = db["students"]
    student_count = students.count_documents({})
    print(f"Students in the collection so far: {student_count}")

    # ************************** Set up the students collection
    students_indexes = students.index_information()
    if 'students_last_and_first_names' in students_indexes.keys():
        print("first and last name index present.")
    else:
        # Create a single UNIQUE index on BOTH the last name and the first name.
        students.create_index([('last_name', pymongo.ASCENDING), ('first_name', pymongo.ASCENDING)],
                              unique=True,
                              name="students_last_and_first_names")
    if 'students_e_mail' in students_indexes.keys():
        print("e-mail address index present.")
    else:
        # Create a UNIQUE index on just the e-mail address
        students.create_index([('e_mail', pymongo.ASCENDING)], unique=True, name='students_e_mail')
    pprint(students.index_information())

    #departments collection setup
    departments = db["departments"]
    department_count = departments.count_documents({})
    print(f"Departments in the collection so far: {department_count}")
    # Defining the schema for the department collection
    department_schema = {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["_id", "abbreviation", "chair_name", "building", "office", "description"],
            "properties": {
                "_id": {
                    "bsonType": "string",
                    "minLength": 10,
                    "maxLength": 50,
                    "description": "Name of the department."
                },
                "abbreviation": {
                    "bsonType": "string",
                    "maxLength": 6,
                    "description": "Abbreviation for the department."
                },
                "chair_name": {
                    "bsonType": "string",
                    "maxLength": 80,
                    "description": "Name of the chair of the department."
                },
                "building": {
                    "bsonType": "string",
                    "enum": ['ANAC', 'CDC', 'DC', 'ECS', 'EN2', 'EN3', 'EN4', 'EN5', 'ET', 'HSCI', 'NUR', 'VEC'],
                    "description": "Building where the department is located."
                },
                "office": {
                    "bsonType": "int",
                    "description": "Office number of the department."
                },
                "description": {
                    "bsonType": "string",
                    "minLength": 10,
                    "maxLength": 80,
                    "description": "Description of the department."
                }
            }
        }
    }
    #db.command("collMod", "departments", validator=department_schema, validationLevel="strict", validationAction="error")
    # ************************** Set up the departments collection
    departments_indexes = departments.index_information()
   # """
    if 'department_names' in departments_indexes.keys(): #department_name
         print("Department name index present.")
    else:
         departments.create_index([('_id', pymongo.ASCENDING)], name="department_names")

    if 'department_abbreviation' in departments_indexes.keys(): #department_abbreviation
         print("department abbreviation index present.")
    else:
         departments.create_index([('abbreviation', pymongo.ASCENDING)], unique=True, name='department_abbreviation')

    if 'department_chair_name' in departments_indexes.keys(): #department_chair_name
         print("chair name index present")
    else:
         departments.create_index([("chair_name", pymongo.ASCENDING)], unique=True, name='department_chair_name')

    #if 'department_building' in departments_indexes.keys(): #department_building
    #     print("building index present")
    #else:
    #     departments.create_index([("building", pymongo.ASCENDING)], unique=False, name='department_building')

    #if 'department_office' in departments_indexes.keys(): #department_office
    #     print("office index present")
    #else:
    #     departments.create_index([("office", pymongo.ASCENDING)], unique=False, name='department_office')

    if 'department_description' in departments_indexes.keys(): #department_description
         print("description index present")
    else:
         departments.create_index([("description", pymongo.ASCENDING)], unique=True, name='department_description')

    if "departments_building_and_office" in departments_indexes.keys():
        print("build and office index present")
    else:
        db.departments.create_index([('building', pymongo.ASCENDING), ('office', pymongo.ASCENDING)], unique=True,
                                    name='departments_building_and_office')
    #"""
    #departments_indexes = departments.index_information()
    """
    departments.create_index([("_id", pymongo.ASCENDING)])
    departments.create_index([("abbreviation", pymongo.ASCENDING)], unique=True)
    departments.create_index([("chair_name", pymongo.ASCENDING)], unique=True)
    departments.create_index([("building", pymongo.ASCENDING), ("office", pymongo.ASCENDING)], unique=True)
    departments.create_index([("description", pymongo.ASCENDING)], unique=True)
    """
    pprint(departments.index_information())
    db.command("collMod", "departments", validator=department_schema) #, validationLevel="strict", validationAction="error"

    main_action: str = ''
    while main_action != menu_main.last_action():
        main_action = menu_main.menu_prompt()
        print('next action: ', main_action)
        exec(main_action)

