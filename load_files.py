import os
import shutil
import sys
import pandas as pd
import subprocess
import re
import json
import copy

# Define the columns
columns = ["submitted", "correct tar", "right files", "Makefile works", 
           "correct distance", "correct format", "erroneous format", "nothing else", "receipt"]
# Define the test cases
test_cases=[
    ['hw1p2', '38.672215864622636', '-121.72280111121437', '38.53874868013882', '-121.7542091083306'],
    ['hw1p2', '38.58681641563053', '-121.55296296578501', '38.53874868013882', '-121.7542091083306']
    #Todo: add more test cases
]
solutions=[9.375873, 11.367878]
# Checking for the presence of specific files
files_to_check = ['hw1p2.cpp', 'Makefile']

# Create an empty DataFrame
grading_df = pd.DataFrame(columns=columns)

################ Functions ##########################


#1. check if tar file works properly
#also moves contents of tar file into the grading folder
def works_properly(source_file):
    command=["tar", "-xvzf", str(source_file),"-C","."]
    print(source_file)
    # print(command)
    # os.system(command)
    # result = subprocess.run(['pwd'], capture_output=True, text=True)
    # print(result.stdout)
    result = subprocess.run(command, capture_output=True, text=True)
    
    # Check if make was successful
    if result.returncode == 0:
        print("Tar works")
        return True, "tar format is correct"
    else:
        print("File format error", result.stderr)
        return False, "tar format is corrupted/wrong"+str(result.returncode)+str( result.stderr)
    
#2. check if the right files are present
def check_if_present(files_to_check):
    grading_dir="."
    #check if right files are present
    files_present = all(os.path.isfile(os.path.join(grading_dir, f)) for f in files_to_check)

    if files_present:
        print("Both hw1p2.cpp and Makefile are present.")
        return True, "Files are in initial directory", "."
    else:
        print("hw1p2.cpp and/or Makefile are missing. Checking for nested director...")
        
        # Check if there is exactly one directory
        directories = [d for d in os.listdir(grading_dir) if os.path.isdir(os.path.join(grading_dir, d))]
        
        if len(directories) == 1:
            print("There is exactly one directory:", directories[0])
            files_present = all(os.path.isfile(os.path.join(grading_dir +"/"+directories[0], f)) for f in files_to_check)
            if files_present:
                print("Both hw1p2.cpp and Makefile are present.")
                return True, "(in nested Directory with name: "+str(directories[0]), directories[0]
            else:
                print("hw1p2.cpp and/or Makefile are missing.")
                return False, "required files (hw1p2.cpp, Makefile) not found.",None
        elif len(directories) > 1:
            print("There are multiple directories present.")
            return False, "complex directory structure. files not located.",None
        else:
            print("There are no directories present.")
            return False, "Where are the files? Files not found in primary or secondary directory.",None
#3. check that the makefile is working
def compile_program(program_dir):
    
    # Change the working directory to the directory
    result = subprocess.run(['make', 'clean'], capture_output=True, text=True)
    print(result)
    # Run the make command
    result = subprocess.run(['make'], capture_output=True, text=True)
    
    # Check if make was successful
    if result.returncode == 0:
        print("Compilation successful")
        return True, "make was successful" #+str(result.returncode)
    else:
        print("Compilation failed:", result.stderr)
        return False, "make had errors:" + str(result.stderr)
    
#4. check that the executable runs
def run_executable(program_dir, test_case):
    # os.chdir(program_dir)
    # Define the path to the executable
    executable_path = copy.deepcopy(test_case)
    #add folder before path if there's an enclosed folder
    executable_path[0]='./' + executable_path[0]#program_dir+'/' + executable_path[0]
    # Run the executable
    try:
        result = subprocess.run(executable_path, capture_output=True, text=True)
    except Exception as e:
        # General exception catch
        print("An error occurred:", e)
        return False, "Unexpected behavior detected. Specifically, this error: " + str(e), str(e)
    print(result.returncode)
    # Output the result
    print(result.stderr)
    print(result.stdout)
    if result.returncode == 0:
        print("Execution successful")
        print("Output:", result.stdout)
        return True, "hw1p2 printout: " + str(result.stdout), str(result.stdout)
    else:
        print("Execution failed:", result.stderr)
        return False, "Executable had an error" + str(result.stderr), str(result.stderr)

#5. check that the correct distance is printed

def check_distance(output, number):
    # Regular expression to find numbers between a colon and a closing brace
    match = re.search(r":\s*([\d\.]+)\s*}", output)
    if match:
        # Convert the matched string to a float and return
        print("Found number: " + str(match.group(1)))
        distance=float(match.group(1))
        if abs(number-distance)<1:
            return True, "Distance: " + str(distance) + "Key: " + str(number)
        else:
            return False, "Distance: " + str(distance) + "Key: " + str(number)
    else:
        # Return None or raise an error if no number is found
        return False, "No number found"


#6. check that the correct json format is used
def check_json(output):
    try:
        # Attempt to parse the string into JSON
        json.loads(output)
        return True, "JSON detected"+ str(output)   # Return True if parsing is successful
    except json.JSONDecodeError:
        return False, "JSON format incorrect"+ str(output) # Return False if an error occurs during JSON decoding
    except TypeError:
        return False, "A type error occured. Here is your output string: " + str(output) # Handle cases where input_string is not a string


#7. check for format error caused by me
def check_if_caused_my_me(output):
    #  pattern = r"\{\s*distance\s*:\s*[\d\.]+\s*miles\s*\}"
    
    # # Search for the pattern in the input string
    # match = re.search(pattern, input_string, re.IGNORECASE)  # re.IGNORECASE to make the search case-insensitive
    
    # if match:
    #     print("Pattern matched:", match.group())
    #     return True
    # else:
    #     print("No match found.")
    #     return False
    match = re.search(r"\{\s*distance\s*:\s*[\d\.]+\s*\}", output)
    if match:
        # Return the extracted key
        return True, str(match.group(0)) + " You had a non-json string but it was likely because you followed my example prior to professor correction. Please use JSON format in the future."
    else:
        # Return None or some error message if no key is found
        print("distance not found")
        return False, " erroneous format not detected. (this is a good thing)"
#8. Check for extra information
def check_if_nothing_more(output):
    print("arbok1")
    try:
        print(output.index("}"), len(output)-1)
    except:
        print("irregular formatting")
        return False, "irregular formatting"
    if "," in output:
        return False, "added extra information with comma in JSON"
    if output.index("}")<len(output)-2:
        
        return False, "appended extra information after the JSON or used complex JSON structure."
    else:
        return True, "no extraneous information detected (This is a good thing.)"

#Teardown student submission after grading
# def clean_directory(directory):
#     # List all files in the directory
#     print(os.listdir(directory))
#     for filename in os.listdir(directory):
#         # Create the full path to the file
#         file_path = os.path.join(directory, filename)
        
#         # Check if it's a file and not a directory
#         if os.path.isfile(file_path):
#             # Get the file extension
#             _, ext = os.path.splitext(filename)
            
#             # If the file is not a Python or CSV file, delete it
#             if ext.lower() not in ['.py', '.csv']:
#                 os.remove(file_path)
#                 print(f"Removed: {filename}")

def clean_directory(directory):
    # List all files and directories in the current directory
    for entry in os.listdir(directory):
        # Create the full path to the entry
        path = os.path.join(directory, entry)
        
        # Check if the path is a directory
        if os.path.isdir(path):
            # Recursively clean the directory
            clean_directory(path)

            # After cleaning, check if the directory is empty and remove it if so
            if not os.listdir(path):
                shutil.rmtree(path)
                print(f"Removed empty directory: {path}")
        else:
            # Get the file extension
            _, ext = os.path.splitext(entry)
            
            # If the file is not a Python or CSV file, delete it
            if ext.lower() not in ['.py', '.csv']:
                os.remove(path)
                print(f"Removed: {entry}")




try:
    source_dir = sys.argv[1]
    print(source_dir)
except:
    print("argv[1] was empty")
    9/0
destination_dir = '.'
clean_directory(destination_dir)
start_dir=os.getcwd()
# Ensure the destination directory exists, create if it doesn't
os.makedirs(destination_dir, exist_ok=True)
# Loop through all files in the source directory
for filename in os.listdir(source_dir):
    os.chdir( start_dir)
    if filename.endswith('.tgz'):

        #gets rid of all files except *.py and grades.csv
        clean_directory(start_dir)
        
        # Construct full file path
        source_file = os.path.join(source_dir, filename)
        destination_file = os.path.join(destination_dir, filename)
        
        new_data={
            "submitted": None, 
            "correct tar": None, 
            "right files": None, 
            "Makefile works": None, 
           "correct distance": None, 
           "correct format": None,
            "erroneous format": None, 
            "nothing else": None, 
            #grading transcript
            "receipt": "Your Grading Receipt:\n"}
        #start of evaluation section
        new_data[columns[0]]=True #if they submitted a tgz file, that's a free point
        #1. Check if tar file works properly
        new_data["receipt"]+="1. Check if tar file works properly: \n"
        credit, feedback = works_properly(source_file)
        new_data[columns[1]]=credit
        new_data["receipt"]+=feedback
        
        #Relevant files should now be in the grading folder
        if not credit:
            #nothing else will work
            #add incomplete row to pandas
            new_data["receipt"]+="Fatal Error: Stopping."
            grading_df.loc[str(filename)] = new_data
            continue
        #2. Check if the right files are present
        
        new_data["receipt"]+="\n2. Check if the right files are present\n"
        #look for if student put the files in tar or behind one folder
        credit, feedback, program_dir = check_if_present(files_to_check)
        
        #add to receipt, register boolean for credit
        new_data[columns[2]]=credit
        new_data["receipt"]+=feedback
        #If not present, stop.
        if not credit:
            #nothing else will work
            #add incomplete row to pandas
            new_data["receipt"]+="Fatal Error: Stopping."
            grading_df.loc[str(filename)] = new_data
            continue
        os.chdir(program_dir)
        #3. check that the makefile is working
        new_data["receipt"]+="\n3. check that the makefile is working\n"
        credit, feedback=compile_program(program_dir)
        new_data[columns[3]]=credit
        new_data["receipt"]+=feedback

        if not credit:
            #nothing else will work
            #add incomplete row to pandas
            new_data["receipt"]+="Fatal Error: Stopping."
            grading_df.loc[str(filename)] = new_data
            continue

        #4. run the executable, get output for later checks
        #TODO: Right now I have it only running on test_case[0] but we ought to have more
        new_data["receipt"]+="\n4. run the executable, get output for later checks\n"
        credit, feedback, output = run_executable(program_dir, test_cases[0])
        # new_data[columns[4]]=credit #leave out because no grading is done at this step
        new_data["receipt"]+=feedback
        if not credit:
            #nothing else will work
            #add incomplete row to pandas
            new_data["receipt"]+="Fatal Error: Stopping."
            grading_df.loc[str(filename)] = new_data
            continue

        new_data["receipt"]+="\n5. check that the correct distance is printed\n"
        credit, feedback = check_distance(output, solutions[0])
        new_data[columns[4]]=credit
        new_data["receipt"]+=feedback

        new_data["receipt"]+="\n6. check that the correct json format is used\n"
        credit, feedback = check_json(output)
        new_data[columns[5]]=credit
        new_data["receipt"]+=feedback

        new_data["receipt"]+="\n7. check for format error \n"
        credit, feedback = check_if_caused_my_me(output)
        new_data[columns[6]]=credit
        new_data["receipt"]+=feedback


        new_data["receipt"]+="\n8. Check for extra information\n"
        credit, feedback = check_if_nothing_more(output)
        new_data[columns[7]]=credit
        new_data["receipt"]+=feedback
        #upload to dataframe
        grading_df.loc[str(filename)] = new_data
        #assignment grading complete
os.chdir( start_dir)
grading_df.to_csv("grades.csv")
        

