git clone [https://github.com/tdvorak07-prog/Programovani.git](https://github.com/tdvorak07-prog/Programovani.git)
cd mydatabase

# Windows
python -m venv venv
.\venv\Scripts\activate
.\venv\Scripts\Activate.ps1

# macOS/Linux
python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt

python manage.py migrate

python manage.py runserver

Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

"D:\Users\dvorakt\desktop\EP4\Maturitni_projekty_EP4A_1.pol\venv\Scripts\python.exe" main.py

python manage.py createsuperuser

python main.py