# LinkShortener

<p align="center">
  <img src="https://user-images.githubusercontent.com/35972878/132550142-b55ce846-ad1c-41a5-89a8-dfabc3a9658d.png" width="555" height="555">
</p>


Website that allows you to create and share shortened links, after inputting your URL. 
Uses Bootstrap for front-end, PostgreSQL for database, Django for back-end, as well as Docker.

# Installation
Requires docker and docker-compose installed  
First, we need to run standalone webapp without DB, so required .env file can be created. Shut application down once it fully loads up.  
`docker-compose -f docker-compose-initial.yml up`  
While in the same directory as dockerfile, use command:  
`docker-compose up`  
Wait until db module loads up fully and shows message in console: `database system is ready to accept connections`, ignore OperationalError error about refused connection in web module  
Launch second console window without shutting down first console window, and find out process id of linkshortener-main_web:  
`docker ps`  
Replace ID below with few first letters of id from previous command for linkshortener-main_web and use command:  
`docker exec -it ID bash`  
Inside launched bash run migrations:   
`python manage.py migrate`  
You can shut down both windows. In new console window, use command to run the application  
`docker-compose up`  
Application can be found at local url:  
`http://localhost:8000/`  


# Tests
Tests for different modules of the application can be run using command:  
`python manage.py test ShortenerIndex API`  



