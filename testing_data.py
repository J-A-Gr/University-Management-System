from app import create_app, db
from app.models import User, Faculty, StudyProgram, StudentInfo
from app.utils.seed import create_hardcoded_admin

# Sukuriame Flask aplikaciją (pvz., naudojant factory funkciją)
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

    faculty2 = Faculty ( name="Fizikos fakultetas", description = "Fakultetas, kuriame mokoma fizikos ir susijusių mokslų." )
    faculty2.generate_code()
    db.session.add(faculty2)
    print ( "Fizikos fakultetas pridėtas" )

    # 2. Studijų programos
    program1 = StudyProgram(name="Informatika", faculty=faculty1)
    program1.generate_code()
    db.session.add(program1)
    print ( "Studijų programa1 pridėta" )

    program2 = StudyProgram(name="Matematika", faculty=faculty2)
    program2.generate_code()
    db.session.add(program2)
    print ( "Studijų programa2 pridėta" )

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
    print("Mokytojas1 pridėtas")

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

    # # 4. Studentai

    # # 5. StudentInfo objektai su grupės kodais

    # 6. Duomenų įrašymas į duomenų bazę
    db.session.commit()