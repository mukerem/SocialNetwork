# Social Network

#### Simple social network with Django and django-rest-framework. 

#### It includes a bot which can demonstrate the functionality of the system according to certain rules.


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
git clone https://github.com/mukerem/SocialNetwork.git
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

Then install all the requirements. The requirement file is contains required python, Django and Django-Rest-Framework (DRF) packages for the project.
```sh
pip install -r requirement.txt
```
But if you are on linux and you are getting an error, try the following command
```sh
pip3 install -r requirement.txt
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
DJANGO_SECRET_KEY = "secret key"
EMAIL_HOST_USER = "YOUR EMAIL"
EMAIL_HOST_PASSWORD = "YOUR PASSWORD"
DB_NAME = "DB NAME"
DB_USER = "DB USER"
DB_PASSWORD = "DB PASSWORD"
DB_HOST = "127.0.0.1"
DB_PORT = "5432"
```
I used my test email to sending an email for users. You can use another email.


##### Step 5: Finally run everything :thumbsup: :rocket:

For the `API`
Now, run migrate to create the model tables in your database


```sh
python manage.py migrate
```

```sh
python manage.py runserver
```


## Bot
The bot is implemeted by using python request library.

The above requirement file include 2 additional libraries used for the Bot. 

If the API and Bot configure in the same machine the above configuration is enough. But if the Bot separate from the API it is required create virtual environment and install 'requests' and 'names' libraries. 

'request' library is used to send a request to the API and 'names' library is used to generate random names, titles and description.

The configuration file required for the bot is found in Bot folder. You can edit the configuration values.
The bot is implemented by using four classes. Such as User, Post, Like and Config. Each classes consists of several methods. The implementation use OOP features such as Inheritance, Encapsulation, and Construtor.

The output of the bot result will display in terminal.

Go to `Bot`
```sh
cd Bot
```

Run the bot
```sh
python3 bot.py
```
