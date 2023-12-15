class Validation():

    #функции для валидации данных
    def check_nameorsurname(name, surname):
        return not (any(chr.isdigit() for chr in name) or any(chr.isdigit() for chr in surname)) 
    def check_group(group):
        allDigits = all(chr.isdigit() for chr in group)
        if not allDigits: 
            return False
        return len(group) == 4
    def check_semester(semester):
        try:
            intSemester = int(semester)
            return (intSemester >= 1 and intSemester <= 7)
        except ValueError:
            return False
    def check_average_mark(avMark):
        floatAverageMark = float(avMark)
        return (floatAverageMark - float(2) > 1e-6 and float(5) - floatAverageMark < 1e-6)
        