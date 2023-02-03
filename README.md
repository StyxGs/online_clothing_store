<h1>Project online clothing store</h1>

<h3>Stack:</h3>
<ul>
<li>Python</li>
<li>PostgreSQL</li>
<li>Redis</li>
</ul>

Local Developing
All actions should be executed from the source directory of the project and only after installing all requirements.

Firstly, create and activate a new virtual environment:

python3.9 -m venv ../venv
source ../venv/bin/activate
Install packages:

pip install --upgrade pip
pip install -r requirements.txt
Run project dependencies, migrations, fill the database with the fixture data etc.:

./manage.py migrate
./manage.py loaddata <path_to_fixture_files>
./manage.py runserver 
Run Redis Server:

redis-server
Run Celery:

celery -A store worker --loglevel=INFO
