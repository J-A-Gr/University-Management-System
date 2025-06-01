from app.extensions import db
from app.models import User, Faculty, StudyProgram, Assessment, ModuleEnrollment, Group, Module, TeacherInfo, StudentInfo
from datetime import datetime, time, timedelta

"""Čia jeigu norite testavimui [pasiseedint duombaze]"""

""" flask shell
>>> from app.utils.seed_data import seed_data
>>> seed_data()
"""


def seed_data():
    try:
        # Fakultetai
        inf_faculty = Faculty.query.filter_by(code="INF").first()
        if not inf_faculty:
            inf_faculty = Faculty(name="Informatikos fakultetas", code="INF", description="Technologijų fakultetas")
            db.session.add(inf_faculty)
            db.session.commit()

        vsf_faculty = Faculty.query.filter_by(code="VSF").first()
        if not vsf_faculty:
            vsf_faculty = Faculty(name="Verslo fakultetas", code="VSF", description="Ekonomikos fakultetas")
            db.session.add(vsf_faculty)
            db.session.commit()

        # Studijų programos
        inf_program = StudyProgram.query.filter_by(code="IFIN").first()
        if not inf_program:
            inf_program = StudyProgram(name="Informatikos inžinerija", code="IFIN", faculty_id=inf_faculty.id)
            db.session.add(inf_program)
            db.session.commit()

        vsf_program = StudyProgram.query.filter_by(code="VSVAD").first()
        if not vsf_program:
            vsf_program = StudyProgram(name="Verslo vadyba", code="VSVAD", faculty_id=vsf_faculty.id)
            db.session.add(vsf_program)
            db.session.commit()

        # Grupės
        group_ifin = Group.query.filter_by(name="IFIN-23-A").first()
        if not group_ifin:
            group_ifin = Group(name="IFIN-23-A", admission_year=2023, group_letter="A", study_program_id=inf_program.id)
            db.session.add(group_ifin)
            db.session.commit()

        group_vsvad = Group.query.filter_by(name="VSVAD-23-A").first()
        if not group_vsvad:
            group_vsvad = Group(name="VSVAD-23-A", admission_year=2023, group_letter="A", study_program_id=vsf_program.id)
            db.session.add(group_vsvad)
            db.session.commit()

        # Admin
        admin = User.query.filter_by(email="admin@uni.lt").first()
        if not admin:
            admin = User(email="admin@uni.lt", first_name="Admin", last_name="User", is_admin=True)
            admin.set_password("admin123")
            db.session.add(admin)

        # Dėstytojas
        teacher = User.query.filter_by(email="teacher@uni.lt").first()
        if not teacher:
            teacher = User(email="teacher@uni.lt", first_name="Tomas", last_name="Mokytojas", is_teacher=True)
            teacher.set_password("teacher123")
            db.session.add(teacher)
            db.session.flush()
        teacher_info = teacher.teacher_info or TeacherInfo.query.filter_by(user_id=teacher.id).first()
        if not teacher_info:
            teacher_info = TeacherInfo(user_id=teacher.id, faculty_id=inf_faculty.id)
            db.session.add(teacher_info)

        # Studentas
        student = User.query.filter_by(email="student@uni.lt").first()
        if not student:
            student = User(email="student@uni.lt", first_name="Sandra", last_name="Studentė", is_student=True)
            student.set_password("student123")
            db.session.add(student)
            db.session.flush()
        student_info = student.student_info or StudentInfo.query.filter_by(user_id=student.id).first()
        if not student_info:
            student_info = StudentInfo(user_id=student.id, study_program_id=inf_program.id, group_id=group_ifin.id, admission_year=2023)
            db.session.add(student_info)

        db.session.commit()

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
                study_program_id=inf_program.id,
                created_by_id=teacher.id,
                teacher_id=teacher_info.id
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
                study_program_id=inf_program.id,
                created_by_id=teacher.id,
                teacher_id=teacher_info.id
            )
            db.session.add(db_module)

        db.session.commit()



        # Užregistruoti studentą į visus aktyvius modulius

        existing_enrollments = ModuleEnrollment.query.filter_by(student_info_id=student_info.id).all()
        enrolled_module_ids = [e.module_id for e in existing_enrollments]

        active_modules = Module.query.filter_by(is_active=True).all()
        for module in active_modules:
            if module.id not in enrolled_module_ids:
                enrollment = ModuleEnrollment(
                    student_info_id=student_info.id,
                    module_id=module.id,
                    semester='rudens' if student_info.current_semester % 2 == 1 else 'pavasario'
                )
                db.session.add(enrollment)

            # Sukuriame vertinimą, jei nėra
            if not module.assessments:
                assessment = Assessment(
                    title="Galutinis egzaminas",
                    description="Pabaigos vertinimas",
                    due_date=datetime.utcnow() + timedelta(days=14),
                    assessment_type="egzaminas",
                    max_points=100,
                    module_id=module.id,
                    created_by_teacher_id=module.teacher_id
                )
                db.session.add(assessment)

        db.session.commit()
        print("Duomenys sėkmingai įrašyti (arba panaudoti esami).")

    except Exception as e:
        db.session.rollback()
        print(f"Klaida kuriant pradinius duomenis: {e}")
