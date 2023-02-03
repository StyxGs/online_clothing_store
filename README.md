<h1>Project online clothing store</h1>

<h3>Stack:</h3>
<ul>
<li>Python</li>
<li>PostgreSQL</li>
<li>Redis</li>
</ul>

<h3>Local Developing</h3>
<p>All actions should be executed from the source directory of the project and only after installing all requirements.</p>
<br/>
<ol>
<li>Firstly, create and activate a new virtual environment:</li>

python3.9 -m venv ../venv
source ../venv/bin/activate
<li>Install packages:</li>

pip install --upgrade pip
pip install -r requirements.txt
<li>Run project dependencies, migrations, fill the database with the fixture data etc.:</li>

./manage.py migrate
./manage.py loaddata <path_to_fixture_files>
./manage.py runserver 
<li>Run Redis Server:</li>

redis-server
<li>Run Celery:</li>

celery -A store worker --loglevel=INFO
</ol>
