from app.models import Group, StudyProgram
from app.extensions import db
from datetime import datetime  # būtina turėti dėl admission year. 

def find_or_create_available_group(study_program_id: int, admission_year: int) -> Group:
    study_program = StudyProgram.query.get(study_program_id)
    base_code = study_program.generate_code()  # gaunam pirmas 4 raides iš sukūrtos funkcijos.
    year_suffix = str(admission_year)[-2:]
    base_name = f"{base_code}-{year_suffix}"  # bazinis grupės pavadinimas.
    group_letter = 'A' # --> tik pradinė raidė

    while True:
        full_group_name = f"{base_name}-{group_letter}"
        group = Group.query.filter_by(name=full_group_name).first() # tikrinam ar tokia grupė jau yra

        if group is None:
            group = Group(
                name=full_group_name,
                admission_year=admission_year,
                group_letter=group_letter,
                study_program_id=study_program_id
            )
            db.session.add(group)
            return group
        elif not group.is_full: # tikrinam ar ne pilna grupė
            return group
        else: # jeigu yra, bet pilna, einam prie sekančios raidės, B, C, D ir t.t. (iki Z)
            # ord() — tai "ordinal" funkcija. Ji paverčia simbolį į jo skaitinį kodą pagal Unicode (arba ASCII). | chr(65)  # grąžina 'A'
            # chr() — tai "character" funkcija. Ji paverčia skaičių atgal į raidę. ||| chr(ord(group_letter) + 1) grąžina 'B'
            group_letter = chr(ord(group_letter) + 1)
            if group_letter > 'Z':
                raise Exception("Visos grupės nuo A iki Z jau pilnos")
