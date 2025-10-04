# 📚 ClassDrop

A minimal, lightweight file sharing API service intended for a university professor to share resource files with their students. Supports uploads and downloads, stores files on disk, and makes it easy to retrieve shared files via a simple HTTP endpoint.

## Dependencies
 - Python 3.10+ (tested on 3.13.3)
 - pip 24+
 - FastAPI
 - Uvicorn

All dependencies are listed in `requirements.txt` — install them with:
```console
pip install -r requirements.txt
```

## Get Started


### 1️⃣ Clone the Repository
```console
git clone https://github.com/maurodeluca/classdrop.git
cd classdrop
```

### 2️⃣ Create a Virtual Environment

It's recommend to use a virtual environmnet to keep dependencies isolated.

```console
python -m venv venv
```

### 3️⃣ Activate the Virtual Environment

On macOS/Linux:

```console
source venv/bin/activate
```

On Windows:
```console
venv\Scripts\activate.bat
````

### 4️⃣ Install Dependencies

All required packages are listed in requirements.txt:

```console
pip install -r requirements.txt
```

### 5️⃣ Run the Server

Start the FastAPI development server 🚀:

```console
fastapi dev main.py
```

The app is served, by default, at http://127.0.0.1:8000, on your local machine.

The app interactive API documentation will be available at:

- http://127.0.0.1:8000/docs (provided by Swagger UI)
- or alternatively http://127.0.0.1:8000/redocs (provided by ReDoc)

