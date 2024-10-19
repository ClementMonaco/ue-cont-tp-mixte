# ue-cont-tp-mixte
This is a small application that manages film reservations for users at a local cinema. The application is composed of 4 micro-services, and the entrypoint for users is the User service. From there, users can consult information about the films on air at their local cinema, rate them, and book reservations online.

The User service is accessible via REST API, and makes requests to the Movies service via GraphQL. It calls to the Booking service via gRPC, which in turns sends requests to the Times Service via gRPC.

![image](https://github.com/user-attachments/assets/8213ad9e-cad6-424a-83b1-cc914ef23804)


To be able to use our software you have to first run each microservice,
Services need to be run in parallel (in different terminals) :

Run movie service :
cd ./UE-AD-A1-MIXTE/movie
python movie.py

Run showtime service :
cd ./UE-AD-A1-MIXTE/showtime
python showtime.py

Run booking service :
cd ./UE-AD-A1-MIXTE/booking
python bookingServer.py

Run user service :
cd ./UE-AD-A1-MIXTE/user
python user.py

You can then use user endpoints from http://127.0.0.1:3203/
Don't hesitate to use http://127.0.0.1:3203/help to know about each endpoint !
