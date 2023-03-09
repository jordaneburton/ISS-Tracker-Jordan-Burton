# Homework 05: Undone (The Sweater Container)
In the previous assignment, homework 04, we created an API for pulling positional and velocity data for the ISS from the web. Now, we will make some improvements on our API as well as add some portability to our app via containerization.
This assignment lets us practice our programming practices, as well as introduces us to using Docker for containerization. Our homework 05 folder contains a python script and a Dockerfile. Once this program is running, we can make queries using `curl` in order to access our various routes and information (for more info, check *Routes and Queries* section).
## Installation
Install the project by cloning the repository. You must also download the `requests`,`flask`, and `xmltodict` libraries for Python3. This can be done using the following commands in the terminal (replace "library" with the desired Python library):
```
$ pip3 install --user library
```
## Program Description
### ISS Tracker
`iss_tracker.py`, contains eight routes that allow us to query various information about the ISS. The data that we are querying is the "Orbital Ephemeris Message" data from the [ISS Trajectory Data](https://spotthestation.nasa.gov/trajectory_data.cfm) website. If you would like to access the XML files we use for the data, it is available [here](https://nasa-public-data.s3.amazonaws.com/iss-coords/current/ISS_OEM/ISS.OEM_J2K_EPH.xml).
When executed, this program will begin to run a Flask development server on the current terminal window. You will need to open a separate window in order to make queries.
### Routes and Queries
In our program, we have eight routes you can use to query information (replace "\<epoch\>" with the entry index number and set limit and offset parameters equal to real integers):
| **Route** | **Method** | **Info Returned** |
|---|---|---|
| `/` | GET | A list of all the data from the set (all Epochs and their positions and velocities) |
| `/epochs` | GET | A list of just the Epochs in the dataset |
| `/epochs?"limit=int&offset=int"` | GET | A modified list of Epochs using query parameters |
| `/epochs/<epoch>` | GET | State vectors for a specific Epoch in the dataset |
| `/epochs/<epoch>/speed` | GET | Instantaneous speed for a specific Epoch |
| `/help` | GET | Help text briefly describing each route |
| `/delete-data` | DELETE | Deletes all data from local dictionary object |
| `/post-data` | POST | Updates local dictionary object with ISS data from the web |
## Using the Existing Docker Image
In your command terminal, you will need to pull my docker image using the following command:
```
$ docker pull jordaneburton/iss_tracker:1.0
```
You can then check to see if the image exists using `docker images`. Once you know you have the image you can run it using the command below:
```
$ docker run -it --rm -p 5000:5000 jordaneburton/iss_tracker:1.0
```
## Building a New Image
In your linux environment, you will first pull the necessary files from my Github. This can be done using `git pull` or whichever preferred method.
There will be a file named `Dockerfile` that you can edit. This can serve as a template for your own docker build. However there are certain commands that must not be changed. *Please do not change from using Python version 3.8.10 and Flask 2.22.0 (unless you are editing the program directly in order that it may run on newer versions).* 
Once you have your finalized your Dockerfile, you can use the following command to build your image:
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
Here is an example of the route for `/epoch/<epoch>/speed`
```
$ curl -X GET localhost:5000/epoch/0/speed
EPOCH entry 0: 2023-048T12:00:00.000Z
Calculated speed to be: 7.658223206788738 km/s
$
```
## Info on ISS Data
The ISS data that we are pulling are the position and velocity of the ISS at certain times. The Epoch is the date and time for the data, but the data itself is given through state vectors. This results in each Epoch having 6 different values (X, Y, Z, X\_DOT, Y\_DOT, Z\_DOT). The X, Y, Z values are positions given in kilometers (km), while the X\_DOT, Y\_DOT, Z\_DOT values are velocities given in kilometers per second (km/s). In addition our `.../speed` route gives the instantaneous speed in km/s.

