<p align="center">
  <img src="https://user-images.githubusercontent.com/35972878/133129972-13608f0f-291e-4207-9d5c-0fd6c2e6899a.png">
</p>

# LinkShortener

<h3> Note: this is a branch used for deployment of heroku preview website of the application. To be able to install application, switch to local-server branch, and use installation instructions there.</h3>  

Website that allows you to create and share shortened links, after inputting your URL. 
Uses Bootstrap for front-end, PostgreSQL for database, Django for back-end, as well as Docker + docker-compose.
Features basic responsiveness, allowing it to look fine on mobile.

# Preview
Website is deployed on Heroku, and functionalities can be tested.  
https://linkshortener-deelite.herokuapp.com/

# Rest API
Website has rest API module, requests can be sent to URL https://linkshortener-deelite.herokuapp.com/api/links/  
API is documented on subsite, where you can check possible actions. https://linkshortener-deelite.herokuapp.com/api/swagger/  

# Installation
Requires docker and docker-compose installed.  
Ensure you are using local-server branch files, if not, switch to that branch.  
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



