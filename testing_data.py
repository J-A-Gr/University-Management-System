from app import create_app, db
from app.models import User, Faculty, StudyProgram, Module, StudentInfo
from app.utils.seed import create_hardcoded_admin
from datetime import time

# Užsikomentuokite ko nenorite testuoti ;)
app = create_app()

with app.app_context():

    db.drop_all()
    db.create_all()

    create_hardcoded_admin()

    # 1. Fakultetai
    faculty1 = Faculty ( name="Informatikos fakultetas", description = "Fakultetas, kuriame mokoma informatikos ir susijusių mokslų." )
    faculty1.generate_code()
    db.session.add(faculty1)
    print ( "fakultetas1 pridėtas" )

    # faculty2 = Faculty ( name = "Fizikos fakultetas", description = "Fakultetas, kuriame mokoma fizikos ir susijusių mokslų." )
    # faculty2.generate_code()
    # faculty2.create_faculty( name = "Fizikos fakultetas", code = "Fizfak", description = "Fakultetas, kuriame mokoma fizikos ir susijusių mokslų." ) # sukuria fakultetą
    # #db.session.add(faculty2)
    # print ( "Fizikos fakultetas pridėtas" )

    # Testing...
    faculty2 = Faculty ( name = "Fizikos fakultetas", description = "Fakultetas, kuriame mokoma fizikos ir susijusių mokslų." )
    #faculty2.create_faculty( name = "Fizikos fakultetas", code = faculty2.generate_code(), description = "Fakultetas, kuriame mokoma fizikos ir susijusių mokslų." ) # sukuria fakultetą
    faculty2.generate_code()
    db.session.add(faculty2)
    print ( "pilnas objektas faculty2: ", faculty2)

    # print ( "žodynas faculty2: ", faculty2.to_dict() )


    # 2. Studijų programos
    program1 = StudyProgram( id = 1, name = "Informatika",  faculty = faculty1 )
    program1.generate_code()
    db.session.add(program1)
    print ( "Studijų programa1 pridėta" )
    print ( program1.code )

    program2 = StudyProgram( id = 2, name = "Matematika", code = "MAT", faculty = faculty2 )
    program2.generate_code()
    db.session.add(program2)
    print ( "Studijų programa2 pridėta" )
    print ( program2.code )
    
    # Programų daugiau
    program1 = StudyProgram( id = 3, name = "Geometrija", faculty = faculty1.id ) 
    program1.generate_code()
    db.session.add(program1)
    print("Studijų programa1 pridėta")
    print(program1.code)
    
    # 3. Mokytojai
    teacher1 = User(
        email="mokytojas1@uni.test",
        first_name="Mokytojas",
        last_name="Vienas",
        is_teacher=True
    )
    teacher1.set_password("GerasSlaptazodis123!")  # Stiprus slaptažodis
    teacher1.ensure_teacher_info()
    db.session.add(teacher1)
    print ("Mokytojas1 pridėtas")
    print (teacher1.first_name)

    teacher2 = User(
        email="mokytojas2@uni.test",
        first_name="Mokytojas",
        last_name="Du",
        is_teacher=True
    )
    teacher2.set_password("LabaiStiprus456!")  # Kitas stiprus slaptažodis
    teacher2.ensure_teacher_info()
    db.session.add(teacher2)
    print("Mokytojas2 pridėtas")
    print(teacher2)

    # 4. Moduliai, būtinai eina po mokytojų, nes moduliai turi priklausyti mokytojams

       # Moduliai
    existing_modules = [m.name for m in Module.query.all()]
    if "Python pagrindai" not in existing_modules:
        python_module = Module(
            name="Python pagrindai",
            description="Įvadas į programavimą su Python",
            credits=6,
            semester="rudens",
            day_of_week="pirmadienis",
            start_time=time(9, 0),
            end_time=time(10, 30),
            room="302",
            study_program_id = program1.id,
            created_by_id = teacher1.id,
            teacher_id = teacher1.id
        )
        db.session.add(python_module)

    if "Duomenų bazės" not in existing_modules:
        db_module = Module(
            name="Duomenų bazės",
            description="SQL, ER modeliai, ORM",
            credits=5,
            semester="pavasario",
            day_of_week="trečiadienis",
            start_time=time(13, 0),
            end_time=time(14, 30),
            room="204",
            study_program_id = program1.id,
            created_by_id = teacher2.id,
            teacher_id = teacher1.id
        )
        db.session.add(db_module)
    if "Algoritmai ir duomenų struktūros" not in existing_modules:
        algo_module = Module(
            name="Algoritmai ir duomenų struktūros",
            description="Pagrindiniai algoritmai ir duomenų struktūros",
            credits=5,
            semester="rudens",
            day_of_week="ketvirtadienis",
            start_time=time(11, 0),
            end_time=time(12, 30),
            room="101",
            study_program_id = program1.id,
            created_by_id = teacher1.id,
            teacher_id = teacher1.id
        )
        db.session.add(algo_module)
    if "Matematikos pagrindai" not in existing_modules:
        math_module = Module(
            name="Matematikos pagrindai",
            description="Pagrindinės matematikos sąvokos ir metodai",
            credits=5,
            semester="rudens",
            day_of_week="penktadienis",
            start_time=time(10, 0),
            end_time=time(11, 30),
            room="A101",
            study_program_id = program2.id,
            created_by_id = teacher2.id,
            teacher_id = teacher2.id
        )
        db.session.add(math_module)
    if "Algebros pagrindai" not in existing_modules:
        algebra_module = Module(
            name="Algebros pagrindai",
            description="Modulis skirtas supažindinti su pagrindinėmis algebros sąvokomis ir metodais.",
            credits=5,
            semester="rudens",
            day_of_week="antradienis",
            start_time=time(10, 0),
            end_time=time(11, 30),
            room="A102",
            study_program_id = program2.id,
            created_by_id = teacher2.id,
            teacher_id = teacher2.id
        )
        db.session.add(algebra_module)

    if "Algebros antra dalis" not in existing_modules:
        algebra_module2 = Module(
            name="Algebros antra dalis",
            description="Modulis skirtas gilinti žinias apie algebrą.",
            credits=5,
            semester="pavasario",
            day_of_week="ketvirtadienis",
            start_time=time(9, 0),
            end_time=time(10, 30),
            room="A103",
            study_program_id = program2.id,
            created_by_id = teacher2.id,
            teacher_id = teacher2.id
        )
        db.session.add(algebra_module2)

    if "Geometrijos pagrindai" not in existing_modules:
        geometry_module = Module(
            name="Geometrijos pagrindai",
            description="Modulis skirtas supažindinti su pagrindinėmis geometrijos sąvokomis ir metodais.",
            credits=5,
            semester="rudens",
            day_of_week="penktadienis",
            start_time=time(11, 0),
            end_time=time(12, 30),
            room="A104",
            study_program_id = program2.id,
            created_by_id = teacher2.id,
            teacher_id = teacher2.id
        )
        db.session.add(geometry_module)


    
    # # NEVEIKIANTIS modulis
    # module3 = Module(
    #     name = "Algebros pagrindai",
    #     description = "Modulis skirtas supažindinti su pagrindinėmis matematikos sąvokomis ir metodais.",
    #     credits = 5,
    #     day_of_week = 'antradienis',
    #     semester = 'rudens',
    #     start_time = '10:00',
    #     end_time = '11:30',
    #     room = "A101",
    #     study_program = program1,  # čia programa1 turi būti jau pridėta prie DB
    #     created_by = teacher1,  # čia mokytojas1 turi būti jau pridėtas prie DB
    #     teacher = teacher1,  # čia mokytojas1 turi būti jau pridėtas prie DB
    #     prerequisite_records = [],  # Pradinė reikšmė, jei nėra privalomų modulių
    # )
    # db.session.add(module2)
    # print("Modulis2 pridėtas")


    # # 4. Studentai

    # pažiūrėti kaip elgiasi programa su vartotoju kuris nepriklauso nei vienai grupei (studentas, mokytojas, administratorius)
    hidden_user = User(
        email = "email1@nui.lt",
        first_name = "Slaptas",
        last_name = "Vartotojas",
        is_student = False,
        is_teacher = False,
        is_admin = False,
    )
    hidden_user.set_password("1111")  # Labai silpnas slaptažodis
    db.session.add(hidden_user)
    print("Slaptas vartotojas pridėtas")    

    # pažiūrėti kaip elgiasi programa su vartotoju kuris priklauso visoms grupėms (studentas, mokytojas, administratorius)
    elite_user = User(
        email = "elite1@nui.lt",
        first_name = "Viešas",
        last_name = "Vartotojas",
        is_student = True,
        is_teacher = True,
        is_admin = True
    )
    elite_user.set_password("EliteP@55!2ej-ž+")  # Labai stiprus slaptažodis
    elite_user.ensure_teacher_info()
    db.session.add(elite_user)
    print("Elitinis vartotojas pridėtas")
    
    student1 = User(
        email = "stud1@uni.lt",
        first_name = "Studentas",
        last_name = "Pirmas",
        is_student = True,
        #birthday = "2001-01-01"  # Pridėta gimimo data
    )
    student1.set_password("1111")  # Stiprus slaptažodis
    #student1.ensure_student_info() # Šitas neveikia!!!
    db.session.add(student1)
    print("Studentas1 pridėtas")

    student2 = User(
        email = "stud2@uni.lt",
        first_name = "Pranas",
        last_name = "Petrauskas",
        is_student = True,
        birthday = "2000-05-15"  # Pridėta gimimo data
    )
    student2.set_password("2222")  # Stiprus slaptažodis
    #student2.ensure_student_info() # Šitas neveikia!!!
    db.session.add(student2)
    print("Studentas2 pridėtas")

    

    # # 5. StudentInfo objektai su grupės kodais

    # 6. Duomenų įrašymas į duomenų bazę
    db.session.commit()

