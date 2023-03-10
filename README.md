# The Great ISS Tracker - Jordan Burton
Previously, we created an API for pulling positional and velocity data for the ISS from the web. Now, we will make some improvements on our API as well as add some convenience for running the application faster.
This assignment lets us practice our programming practices, as well as provides us more practice with using Docker for containerization. This assignment has its own repository separate from other assignments. It contains a python script, a Dockerfile, and a Docker Compose file. Once this program is running, we can make queries using `curl` in order to access our various routes and information (for more info, check *Routes and Queries* section).
## Installation
Install the project by cloning the repository. Downloading libraries for this application is not necessary thanks to Docker's containerization. When ran via docker commands, the necessary libraries will be included for the API.
## Program Description
### ISS Tracker
`iss_tracker.py`, contains thirteen routes that allow us to query various information about the ISS. The data that we are querying is the "Orbital Ephemeris Message" data from the [ISS Trajectory Data](https://spotthestation.nasa.gov/trajectory_data.cfm) website. If you would like to access the XML files we use for the data, it is available [here](https://nasa-public-data.s3.amazonaws.com/iss-coords/current/ISS_OEM/ISS.OEM_J2K_EPH.xml).
When executed, this program will begin to run a Flask development server on the current terminal window. You will need to open a separate window in order to make queries.
### Routes and Queries
In our program, we have thirteen routes you can use to query information (replace "\<epoch\>" with the entry index number and set limit and offset parameters equal to real integers):
| **Route** | **Method** | **Info Returned** |
|---|---|---|
| `/` | GET | A list of all the data from the set (all Epochs and their positions and velocities) |
| `/epochs` | GET | A list of just the Epochs in the dataset |
| `/epochs?"limit=int&offset=int"` | GET | A modified list of Epochs using query parameters |
| `/epochs/<epoch>` | GET | State vectors for a specific Epoch in the dataset |
| `/epochs/<epoch>/speed` | GET | Instantaneous speed for a specific Epoch |
| `/epochs/<epoch>/location` | GET | Geolocation for a specified Epoch |
| `/help` | GET | Help text briefly describing each route |
| `/delete-data` | DELETE | Deletes all data from local dictionary object |
| `/post-data` | POST | Updates local dictionary object with ISS data from the web |
| `/comment` | GET | A list of comments from the dataset |
| `/header` | GET | The header for the dataset |
| `/metadata` | GET | Metadata from the dataset |
| `/now` | GET | Geolocation of the Epoch closest to the current time |
## Using the Existing Docker Image
Before you can run the application, you will need to pull the repository for this project off of GitHub using `git pull` or any other preferred method. In your command terminal, you will need to pull my docker image using the following command:
```
$ docker pull jordaneburton/iss_tracker:2.0
```
You can then check to see if the image exists using `docker images`. Once you know you have the image you can run it using either of the commands below:
```
$ docker-compose up
...
OR
...
$ docker run -it --rm -p 5000:5000 jordaneburton/iss_tracker:2.0
```
## Building a New Image
In your linux environment, you will first pull the necessary files from my Github. This can be done using `git pull` or whichever preferred method.
There will be a file named `Dockerfile` that you can edit. This can serve as a template for your own docker build. However there are certain commands that must not be changed. *Please do not change from using Python version 3.8.10 and Flask 2.22.0 (unless you are editing the program directly in order that it may run on newer versions).* 
Since this version of the project has a docker-compose file, we can use that to speed up the process of building and running the application. Now you can just use the following command to both build and run the API:
```
$ docker-compose up --build
```
However, if you would prefer to do it another way, or the previous way isn't working, you can still use this method. Once you have your finalized your Dockerfile, you can use the following command to build your image:
```
$ docker build -t <username>/iss_tracker:<tag> .
```
Once built, you can use the following commands to find your image and run it:
```
$ docker images
...
...
$ docker run -it --rm -p 5000:5000 <username>/iss_tracker:<tag> 
```
## Running the Code
In order to properly run this program, you will need to open two terminal windows. After running the docker image, your window should look like this:
```
...
...
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
 * Running on http://172.17.0.2:5000    <--- if 'localhost' does not work for route commands,
Press CTRL+C to quit			     try using this IP address
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: 101-492-104
...
...
```
Now, open a second terminal window and try to make a query using the following route:
```
$ curl -X GET localhost:5000/help
```
This route returns all of the available routes for our program along with brief descriptions of their usage. After using that command, your window should look similar to this:
```
usage: curl -X [METHOD] [localhost ip]:5000/[ROUTE]

A Flask API for obtaining ISS position and velocity data

Methods:
  GET     Used for all but two routes. Retrieves information
  DELETE  Used for /delete-data. Method for deletion
  POST    Used for /post-data. Method for updating info

Routes:
  /                 Returns all data from ISS
  /epochs           Returns list of all Epochs in ISS dataset
...
...
```
In order to make queries you will want to follow the format shown in the beginning of the help route, by including the **METHOD**. The routes for `/delete-data` and `/post-data` have different METHODS than the rest of the routes so pay close attention to your commands. 
Here is an example of the route for `/epoch/<epoch>/location`
```
$ curl -X GET localhost:5000/epoch/0/location
Epoch Entry: 2023-067T12:00:00.000Z
ISS Location: the Ocean
$
```
## Info on ISS Data
The ISS data that we are pulling are the position and velocity of the ISS at certain times. The Epoch is the date and time for the data, but the data itself is given through state vectors. This results in each Epoch having 6 different values (X, Y, Z, X\_DOT, Y\_DOT, Z\_DOT). The X, Y, Z values are positions given in kilometers (km), while the X\_DOT, Y\_DOT, Z\_DOT values are velocities given in kilometers per second (km/s). In addition our `.../speed` route gives the instantaneous speed in km/s.
Most other routes will further interpret the results if calculation is required. But for some routes that directly return lists or dictionaries of data, just know that any positional data is in kilometers and any velocity data is in kilometers per second.

