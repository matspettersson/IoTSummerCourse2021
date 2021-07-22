python3 -m there ls -l /flash/*
python3 -m there rm /flash/boot.py
python3 -m there rm /flash/main.py
python3 -m there ls -l /flash/*
python3 -m there push boot.py /flash
python3 -m there push main.py /flash
python3 -m there ls -l /flash/*
