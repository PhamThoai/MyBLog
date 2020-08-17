# Django Blog API

A blog system based on `Python 3.7.3` and `Django3.0.8`.

## Main Features:
- All app:  posts, comments, images, tags, accounts
- Posts support `Markdown`
- OAuth Login supported, including Google, Facebook.
- Register and login using username and password
- send confirmation email
- Support pagination, search for posts, tags, accounts
- processes and stores images in suitable sizes

## Dependencies

* django
* djangorestframework
* django-rest-framework-social-oauth2
* pillow
* markdown
* python-slugify

## Run the project locally
1. Clone the project to local

   Open the command line, go to the folder where the project is saved, and enter the following command:

   ```
   git clone https://github.com/zmrenwu/django-blog-tutorial.git
   ```
2. Create and activate a virtual environment

   Go to the folder where the virtual environment is saved on the command line and enter the following command to create and activate the virtual environment:

   ```
   python -m venv venv

   # windows cmd.exe
   venv\Scripts\activate.bat
  
   # windows PowerShell
   venv\Scripts\Activate.ps1

   # linux
   source venv/bin/activate
   ```
3. Install project dependencies
   Make sure the virtual environment is activated
   
   ```
   pip install -r requirements.txt
   ```
4. Migrate the database

   ```
   python manage.py makemigrations
   python manage.py migrate
   ```

5. Create background administrator account

   ```
   python manage.py createsuperuser
   ```
   
6. Run the development server

   ```
   python manage.py runserver
   ```

   development server at http://127.0.0.1:8000/
