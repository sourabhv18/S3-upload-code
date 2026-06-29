from pathlib import Path


def inventory(folder_path):
    folder_path= Path(folder_path)
    count={}
    size = {}

    for each_file in folder_path.iterdir():
        if not each_file.is_file():
            continue
            
        ext =each_file.suffix if each_file.suffix else 'no_extension'

        count[ext] = count.get(ext,0)+ 1
        size[ext] = (size.get(ext,0)+ each_file.stat().st_size)/1024

    return count, size


if __name__ =="__main__":
    folder=Path(r'D:\Downloads')
    count, size = inventory(folder)

    print("Counts: ", count)
    print("Sizes (bytes): ", size)