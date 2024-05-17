import pandas as pd
import re
import sys

# Define the columns
columns = ["submitted", "correct tar", "right files", "Makefile works", 
           "correct distance", "correct format", "erroneous format", "nothing else", "receipt"]
# def find_score(name, csv_path):
#     # Load the CSV into a DataFrame
#     df = pd.read_csv(csv_path, index_col=0)  # Assuming the first column is the index with labels

#     # Normalize the name for searching
#     normalized_name = name.lower().replace(" ", "")

#     # Attempt to find a row label matching the normalized name
#     matched_row = None
#     for label in df.index:
#         # Normalize the label and look for a name match
#         normalized_label = re.sub(r"[^a-zA-Z]", "", label).lower()
#         if normalized_name in normalized_label:
#             matched_row = label
#             break

def find_correct_label(labels, name):
    correct_labels = []
    index=-1
    correct_index=-1
    for label in labels:
        index+=1
        label_lower = label.lower()
        
        name_words = name.lower().split()
        
        if all(word in label_lower for word in name_words):
            correct_labels.append(label)
            correct_index=index
            break
    
    if len(correct_labels) == 1:
        return correct_index
    elif len(correct_labels) == 0:
        raise ValueError("No correct label found.")
    else:
        raise ValueError("Multiple correct labels found.")



#     if matched_row:
#         # Calculate the score: Assuming True = 1 point, False = 0 points
#         score = df.loc[matched_row].sum()
#         print(f"Match found for {name} in row {matched_row}: Score = {score}")
#         return score
#     else:
#         print("No match found for", name)
#         return None

def compute_grade(frames):
    score=1
    if frames[columns[0]]==True:
        score+=1
    if frames[columns[1]]==True:
        score+=1
    if frames[columns[2]]==True:
        score+=1
    if frames[columns[3]]==True:
        score+=2
    if frames[columns[4]]==True:
        score+=2
    if frames[columns[5]]==True or frames[columns[6]]==True:
        score+=1
    if  frames[columns[7]]==True:
        score+=1
    return score

def find_score(name, csv_path):
    df = pd.read_csv(csv_path, index_col=0)
    
    # Create a list of normalized labels
    labels = [label.lower() for label in df.index]
    
    index=find_correct_label(labels, name)
    df = pd.read_csv(csv_path, index_col=0)
    return compute_grade(df.loc[df.index[index]][:-1]), df.loc[df.index[index]][-1]

try:
    csv_path = 'grades.csv'
    name = sys.argv[1]
    score, reciept=find_score(name, csv_path)
    print("Grade: " + str(score)+"\n"+ reciept)
except Exception as e:
    # General exception catch
    print("An error occurred:", e)
