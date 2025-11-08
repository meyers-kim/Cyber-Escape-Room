# Cyber Escape Room: Shared Task

University of Luxembourg — Programming Fundamentals (Group 8)

Group members:
- Nmili Souhail - Worked on the malware and vault room
- Ermakova Mariia - Worked on the soc and dns room
- Meyers Kim Justin - Worked on the gameengine and the final room

---

## Description

This project is a small text-based **Cyber Escape Room** written in Python.  
It was created by students of the University of Luxembourg as part of the Programming Fundamentals course (Semester 1 - Master in Cybersecurity and Cyber Defence).  
The idea is to move through several rooms (SOC, DNS, Vault, Malware, Final) and solve short cybersecurity challenges.  
Each room gives one token, and once all four tokens are collected, they can be combined at the Final Gate to escape.

The game runs in the terminal and uses a simple REPL (read-eval-print-loop) structure.  
All progress can be saved and loaded, and every playthrough is logged to a transcript file that follows a specific format for grading.

---

## How to Run

### Requirements
- Python 3.8 or newer
- No external libraries needed (only built-in modules)

### Start the game
In a terminal, go to the project folder and run:

```bash
python escape.py
```

You can also specify the start room and transcript name:

```bash
python escape.py --start intro --transcript run.txt
```

By default:
- Transcript files are saved in the `transcripts/` folder  
- Game saves are stored in the `saves/` folder  

### Load a save file directly from start
If you already have a saved game and want to continue it right away,  
you can provide the save file when starting the game (you need to enter the exact save file name with .json, if the name is wrong the game will just start fresh):

```bash
python escape.py --load saves/my_save.json
```

This will automatically restore your previous progress (room, tokens, and flags)  
and continue the game from where you left off.

You can also combine both commands by starting in a desired room with a desired save file.

---

## Commands

| Command | Description |
|----------|-------------|
| `look` | Describe the current room and see available items |
| `move <room>` | Move to another room (intro, soc, dns, vault, malware, final) |
| `inspect <item>` | Inspect a file in the current room to extract a token |
| `use <item>` | Use something (for example: `use gate` in the final room) |
| `hint` | Get a short description of what to do in the current room |
| `inventory` | Show collected tokens |
| `save <name>` | Save your progress (stored in `saves/<name>.json`) |
| `load <name>` | Load a previously saved file |
| `quit` | Quit the game (asks for confirmation) |

---

## Saving and Loading

You can save the game at any point:
```
save myprogress
```
It will be saved as `saves/myprogress.json`.

To load it again:
```
load myprogress
```

---


## Testing the Game

To test everything, you can try the following sequence:

```
python escape.py --start intro --transcript run_test.txt
look
hint
move soc
inspect auth.log
move dns
inspect dns.cfg
move vault
inspect vault_dump.txt
move malware
inspect proc_tree.jsonl
inventory
move final
inspect final_gate.txt
use gate
```

You should see the final message saying the proof was accepted and the game will close automatically.