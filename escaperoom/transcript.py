class Transcript:
    # handles writing stuff to run.txt

    def __init__(self, path="run.txt"):
        self.path = path
        self._fh = open(path, "w", encoding="utf-8")

    def log(self, line):
        # write a single line and flush it right away
        self._fh.write(line.rstrip() + "\n")
        self._fh.flush()

    def close(self):
        # close file when game ends
        self._fh.close()