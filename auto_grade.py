from grade import find_score
import sys

def get_from_file(filename):
    with open(filename, 'r') as test_file:
        full_file=test_file.read()
    return full_file
class_list_file = sys.argv[1]
roster=get_from_file(class_list_file).split("\n")
csv_path = 'grades.csv'
try:
    assert sys.argv[2]=="receipt"
    print("ekans")
    for student in roster:
        print(student)
        try:
            score, receipt=find_score(student, csv_path)
        except:
            score=0
            receipt="No Submission."
        print(student, score)
        print("\n")
        print(receipt)
except:
    print("arbok")
    for student in roster:
        print(student)
        try:
            score, _=find_score(student, csv_path)
        except:
            score=0
            receipt="No Submission."
        print(student, score)
        print("\n")