from pathlib import Path
import subprocess


INPUT_FOLDER = r"D:\Documents\EDFS_Esigs\For_Cleaning"

# recursively find all jpg files
files = Path(INPUT_FOLDER).rglob("*.jpg")

for file in files:

    # gets:
    # 14_OSAO
    # 13_GHQTS
    # etc...
    folder_name = file.parent.name

    output_folder = f"samples\\{folder_name}"

    command = (

        f'python -m backend.main "{file}" '
        f'--output "{output_folder}"'

    )

    print(command)

    subprocess.run(command, shell=True)

print("\nFinished!")