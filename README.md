# Social Network

### Simple social network with Django and django-rest-framework. 

### It includes a bot which can demonstrate the functionality of the system according to certain rules.


This is a brief guide on how to configure social netowrk API and bot on your machine.

Before any installation make sure you have the latest version of Python 3 installed on your machine and the path is configured properly, also since we are using a virtual environment make sure you you have virtual environment of your choice.

But if you don't have a virtual environment install it using the following command first.

Mainly the OS on your machine should be a linux based OS. This means all the following commands are not guaranteed to work on Windows machine.
```sh
pip install virtualenv
```

#### Step 1: Create a folder that will contain everything, then go into the folder :file_folder:

#### Step 2: Now pull the necessary files from github :arrow_double_down:

The following clones the backend
```sh
git clone https://github.com/SocialNetwork.git
```

#### Step 3: We are almost there, just a few configurations left :tired_face:

Now create a virtual environment
```sh
python -m virtualenv env
```
But if you are on linux and you are getting an error, try the following command
```sh
python3 -m virtualenv env
```
This will create a vritual environment named `env` inside in project folder.

Activate the virtual environment
For linux
```sh
source env/bin/activate
```

Then install all the requirements. The requirement file is contains required python, Django and Djago-Rest-Framework (DRF) packages for the project.
```sh
pip install -r requirements.txt
```
But if you are on linux and you are getting an error, try the following command
```sh
pip3 install -r requirements.txt
```

##### Step 4: Last Configuration, configuring the environment variable
First configure your database, the project uses postgres by default, but you can use mysql or any other django supported databases

Go to `API`
```sh
cd API
```

Then create a `.env` file
```sh
touch .env
```

Then open the `.env` file and change the following variables by your database configurations.

```
DJANGO_SECRET_KEY = "django-insecure-8ag)(e328p06u$b@wgq4s5n*570wye1)=_i=-)i&y%qfhi(et8"
EMAIL_HOST_USER = "rapi8work@gmail.com"
EMAIL_HOST_PASSWORD = "adnan@887"
DB_NAME = "socialnetwork"
DB_USER = "mukerem"
DB_PASSWORD = "adnan0887"
DB_HOST = "127.0.0.1"
DB_PORT = "5432"
```
I used my test email to sending an email for users. You can use another email.

Now, run migrate to create the model tables in your database

```sh
cd aoj-backend
```

```sh
python manage.py migrate
```
