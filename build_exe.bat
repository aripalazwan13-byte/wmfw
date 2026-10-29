@echo off
python -m pip install --upgrade pip
python -m pip install -r requirements.txt pyinstaller
python -m PyInstaller --noconfirm --onefile --windowed --name PhotoSorter photo_sorter.py
echo.
echo Selesai. File EXE ada di folder dist.
pause
