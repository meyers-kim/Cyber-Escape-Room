import os

class Transcript:
    # handles writing stuff to run.txt

    def __init__(self, path="run.txt"):
        # if the user only gave a filename store it in transcripts/
        dirname = os.path.dirname(path)
        basename = os.path.basename(path)

        if not dirname:
            dirname = "transcripts"

        # ensure the directory exists
        os.makedirs(dirname, exist_ok=True)

        # final full path
        full_path = os.path.join(dirname, basename)
        self.path = full_path

        # open file for writing
        self._fh = open(full_path, "w", encoding="utf-8")

    def log(self, line):
        # write a single line and flush it right away
        self._fh.write(line.rstrip() + "\n")
        self._fh.flush()

    def close(self):
        # close file when game ends
        try:
            self._fh.close()
        except Exception:
            pass