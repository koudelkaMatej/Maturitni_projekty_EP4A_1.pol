git clone [https://github.com/tdvorak07-prog/Programovani.git](https://github.com/tdvorak07-prog/Programovani.git)
cd mydatabase

# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt

python manage.py migrate

python manage.py runserver