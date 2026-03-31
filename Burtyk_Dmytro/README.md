# Flux Electronics

## Installation

**1. Clone the repository**
```bash
git clone [https://github.com/yourusername/flux-electronics.git](https://github.com/yourusername/flux-electronics.git)
cd flux-electronics

# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt

python manage.py migrate

python manage.py runserver