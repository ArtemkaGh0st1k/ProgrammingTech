from CourseWork import *
import unittest
import re

class Test_CourseWork(unittest.TestCase):
    def test_DataBaseToNull(self): 
        check = True
        
        db = sqlite3.connect('server.db')
        sql = db.cursor()

        sql.execute("""SELECT * FROM student WHERE rowid == 1""")

        for elem in sql.fetchall():
            if (elem[0] != None 
                and elem[1] != None 
                and elem[2] != None
                and elem[3] != None
                and elem[4] != None
                and elem[5] != None):
                    check = True
        
        db.close()

        self.assertEqual(first=check, second=True)

    def test_DataBaseToNameAndSurname(self):
        check = True
        
        db = sqlite3.connect('server.db')
        sql = db.cursor()

        sql.execute("""SELECT name_first, name_last FROM student""")

        all_names = list()
        all_surnames = list()
        for elem in sql.fetchall():
             all_names.append(elem[0])
             all_surnames.append(elem[1])

        for name in all_names:
            if (re.search('\d\W', name)) != None:
                check = False
                self.assertEqual(first=check, second=True)
                db.close()
                return
        
        for surname in all_surnames:
            if (re.search('\d\W', surname)) != None:
                check = False
                self.assertEqual(first=check, second=True)
                db.close()
                return
        
        db.close()

        self.assertEqual(first=check,second=True)

    def test_DataBaseToSemmestr(self):
        check = True
    
        db = sqlite3.connect('server.db')
        sql = db.cursor()

        sql.execute("""SELECT semmestr FROM student""")

        all_semmestr = list()
        for elem in sql.fetchall():
                all_semmestr.append(elem[0])

        for semm in all_semmestr:
                if ((semm < 1 or semm >7) 
                    or (re.search(r'\D\W', str(semm)) !=None)):
                    check = False
                    self.assertEqual(first=check, second=True)
                    db.close()
                    return
                
        db.close()
        
        self.assertEqual(first=check, second=True)

    def test_DataBaseToAverageMark(self):
        check = True
    
        db = sqlite3.connect('server.db')
        sql = db.cursor()

        sql.execute("""SELECT average_mark FROM student""")

        all_avg_marks = list()
        for elem in sql.fetchall():
            all_avg_marks.append(elem[0])
        
        for avg in all_avg_marks:
            if ((re.search('-', str(avg)) != None)
                or (re.search(r'\D\W', str(avg)) != None)):
                check = False
                self.assertEqual(first=check, second=True)
                db.close()
                return

        db.close()

        self.assertEqual(first=check, second=True)
        
    def test_DataBaseToGroup(self):
        check = True
        
        db = sqlite3.connect('server.db')
        sql = db.cursor()

        sql.execute("""SELECT name_group FROM student""")

        all_groups = list()
        for elem in sql.fetchall():
            all_groups.append(str(elem[0]))

        for group in all_groups:
            if (re.search(r'\D\W', group) != None):
                check = False
                self.assertEqual(first=check, second=True)
                db.close()
                return
        
        db.close()
        
        self.assertEqual(first=check, second=True)
                   
        

    