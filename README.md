## SPA application: Comments.

## [Deploy](https://dzencode-comments-hy2f.onrender.com/)

Our web application for Comments is built using the Django framework and the Vue.js frontend library. It allows users to add comments and engage in conversations on our website without registration, but with the requirement of entering valid information (including CAPTCHA). This file provides detailed instructions on how to install and run our web application.

## Installation:

1. Clone the project repository to your computer:

   ```bash
   git clone https://github.com/legendarym4x/dZENcode_Comments.git

2. Create and activate a virtual environment for the project:

   ```bash
   python -m venv venv
   venv\Scripts\activate - for Windows;
   source venv/bin/activate - for Linux/MacOS.
   
3. Install the dependencies specified in requirements.txt:

   ```bash
   pip install -r requirements.txt
   
4. Create and fill in the .env file (in the directories where the `manage.py` is located), leaving the 
"DB_HOST=comments-postgres" field as is:

   ```bash
   SECRET_KEY=...

   DB_NAME=...
   DB_USER=...
   DB_PASSWORD=...
   DB_HOST=comments-postgres
   DB_PORT=...
   
5. Go to the directory where the Dockerfile and docker-compose.yml files are located and run the command:

   ```bash
   docker-compose up --build
   
6. After running the containers, you need to run the commands to create the tables in the database.
Log in to the web application container:

   ```bash
   docker-compose exec web /bin/sh
   
7. Run migrations:

   ```bash
   python manage.py migrate

8. Create a superuser:

   ```bash
   python manage.py createsuperuser
   
9. Exit the container.

10. Go to the admin panel and create the first post (for this we added a superuser). The post must be published and 
have the status "Published":

    ```bash
    http://127.0.0.1:8000/admin
  
 
11. Go to our app page and start chatting :)

    ```bash
    http://127.0.0.1:8000/


 ## Usage:


The application provides the following functions:

- Adding comments: Users can add new comments by specifying their name, email address, website, comment text, and uploading images or text files.

- Sorting of comments: Comments can be sorted by the author's name, e-mail address or date of addition. Sorting is possible both in ascending and descending order. The default sorting is LIFO.

- Reply to comments: Users can leave replies to existing comments.

- Pagination: Comments are divided into pages for ease of navigation. By default - 25 comments per page.

- Captcha: Captcha is provided for security of access to adding comments.

- Uploading images and files: Users can upload images and text files to their comments.
 > The image must be no more than 320x240 pixels, if requested it will be filled
the image is larger, the image is proportional
decreases to the given size. Acceptable file formats: JPG, GIF, PNG.

 > The text file must be no more than 100 Kb. Acceptable file formats: TXT.

 > Posts, comments and users are saved in the database.