"""Transcript writer for the game.
Creates transcripts/<file> if only a name is given.
We append lines as the player plays."""

import os

class Transcript:
    """Handles writing the run transcript.
    We keep the file handle open during the game and flush on each line.
    The engine calls close() when the game ends."""

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