import sys
import shutil

if __name__ == "__main__":
    dir = sys.argv[1]
    shutil.rmtree(dir)
