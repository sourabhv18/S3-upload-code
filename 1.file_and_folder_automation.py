import os 
from pathlib import Path

folder=Path(r'D:\Logs')
Total_files=0
## To check if folder exists

if os.path.exists(folder):
    print("Folder exists")
    for each_file in folder.iterdir():
        Total_files+=1
    print(f"Total files in folder: {Total_files}")

else:
    print("Folder does not exist, creating folder")
    os.mkdir(folder)

    file=folder/"Status.txt"
    with open(file, "w") as c:
        c.write(f"Checked Successfully at {file}")