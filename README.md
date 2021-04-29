### Setup
1. Create a folder and put all the files inside it.
2. Create a virtual environtment - `virtualenv env`
3. Activate VirtualENV - `source env/bin/activate`
4. Write out environment variables like in example.py
5. Run requirements.txt - `pip3 install -r requirements/base.txt`
6. Run migrations - `python3 manage.py migrate`
7. Create superuser - `python3 manage.py createsuperuser`
8. Run the Application - `python3 manage.py runserver`
9. Go to - http://localhost:8000/