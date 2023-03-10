from flask import Flask, request
import requests
import xmltodict
import math
import time
import geopy
from geopy.geocoders import Nominatim

app = Flask(__name__)
global iss_data
global iss_header
global iss_metadata

def request_nasa_data():
    """
    Function for pulling ISS data from NASA website
    """
    iss_url = 'https://nasa-public-data.s3.amazonaws.com/iss-coords/current/ISS_OEM/ISS.OEM_J2K_EPH.xml'
    response = requests.get(iss_url)
    iss_response = xmltodict.parse(response.text)
    
    global iss_data 
    global iss_header
    global iss_metadata
    iss_data = iss_response['ndm']['oem']['body']['segment']['data']
    iss_header = iss_response['ndm']['oem']['header']
    iss_metadata = iss_response['ndm']['oem']['body']['segment']['metadata']

def epoch_to_datetime(epoch: str) -> list:
    """
    Parses through the epoch string and returns a list of only the numbers
    List format: [year, day, hour, minute, second]
    """
    res_time = []
    for i in epoch:
        if i.isnumeric():
            res_time.append(float(i))
    year = res_time[0]*1000 + res_time[1]*100 + res_time[2]*10 + res_time[3]
    day = res_time[4]*100 + res_time[5]*10 + res_time[6]
    hour = res_time[7]*10 + res_time[8]
    minute = res_time[9]*10 + res_time[10]
    second = res_time[11]*10 + res_time[12] + res_time[13]/10 + res_time[14]/100 + res_time[15]/1000
    
    res_time = [year, day, hour, minute, second]
    return res_time

request_nasa_data()

@app.route('/', methods=['GET'])
def get_data() -> list:
    """
    Returns list of all the data from the dataset
    """
    if iss_data == {}:
        return 'Error: Data cleared. Fetch new data with /post-data \n'
    else:
        result = []
        stateVectors = []
        for i in iss_data['stateVector']:
            stateVectors.append(i['EPOCH'])
            stateVectors.append('X = ' + i['X']['#text'] + i['X']['@units'])
            stateVectors.append('Y = ' + i['Y']['#text'] + i['Y']['@units'])
            stateVectors.append('Z = ' + i['Z']['#text'] + i['Z']['@units'])
        
            stateVectors.append('X_DOT = ' + i['X_DOT']['#text'] + i['X_DOT']['@units'])
            stateVectors.append('Y_DOT = ' + i['Y_DOT']['#text'] + i['Y_DOT']['@units'])
            stateVectors.append('Z_DOT = ' + i['Z_DOT']['#text'] + i['Z_DOT']['@units'])
        
            result.append(stateVectors)
            stateVectors = []
        return result

@app.route('/epochs', methods=['GET'])
def epoch() -> list:
    """
    Parses through epochs and returns all epochs. Search can be modified via 
    'limit' and 'offset' parameters.

    Returns a list of desired epochs
    """
    if iss_data == {}:
        return 'Error: Data cleared. Fetch new data with /post-data \n'
    else:
        limit = request.args.get('limit', 0)
        offset = request.args.get('offset', 0)
        if limit or offset:
            try:
                limit = int(limit)
                offset = int(offset)
            except ValueError:
                return 'Error: Invalid input - limit and offset must be numeric \n'
        
        list_epochs = []
        epoch_i = ''
        offset_iter = 0
        limit_iter = 0

        if (offset < 0):
            offset = 0
        if (limit < 0):
            limit = 0
        for i in iss_data['stateVector']:
            if (offset_iter < offset):
                offset_iter += 1
                continue
            epoch_i = i['EPOCH']
            list_epochs.append(epoch_i)
            if (limit > 0):
                limit_iter += 1
                if (limit_iter >= limit):
                    break
        return list_epochs

@app.route('/epochs/<int:epoch>', methods=['GET'])
def get_epoch(epoch) -> list:
    """
    Parses and finds data for a single specified epoch. Epoch can be specified 
    by its 'index' (e.g. 0, 1,...) 

    Returns data for a specified epoch
    """
    if iss_data == {}:
        return 'Error: Data cleared. Fetch new data with /post-data \n'
    else:
        if (epoch < 0) or (epoch > len(iss_data['stateVector']) - 1):
            return 'Error: Epoch entry index is out of range \n'
        result = ('EPOCH entry {}: {}\n'
                .format(epoch, iss_data['stateVector'][epoch]['EPOCH']))
        return result

@app.route('/epochs/<int:epoch>/speed', methods=['GET'])
def get_speed(epoch) -> str:
    """
    Finds a specified epoch and calculates the instantaneous speed of the ISS
    using the data from said epoch

    Returns speed calculated from specified epoch's data
    """
    if iss_data == {}:
        return 'Error: Data cleared. Fetch new data with /post-data \n'
    else:
        x_dot = float(iss_data['stateVector'][epoch]['X_DOT']['#text'])
        y_dot = float(iss_data['stateVector'][epoch]['Y_DOT']['#text'])
        z_dot = float(iss_data['stateVector'][epoch]['Z_DOT']['#text'])
        units = str(iss_data['stateVector'][epoch]['Z_DOT']['@units'])

        speed = math.sqrt(x_dot**2 + y_dot**2 + z_dot**2)
        result = ('EPOCH: {}\nCalculated speed to be: {} {}\n'
                .format(iss_data['stateVector'][epoch]['EPOCH'],speed, units))
        return result

@app.route('/help', methods=['GET'])
def help() -> str:
    """
    Help function that returns all commands/routes usable with the program
    along with a brief description of desired usage
    """

    return """usage: curl -X [METHOD] [localhost ip]:5000/[ROUTE]

A Flask API for obtaining ISS position and velocity data
    
Methods:
  GET     Used for all but two routes. Retrieves information
  DELETE  Used for /delete-data. Method for deletion
  POST    Used for /post-data. Method for updating info

Routes:
  /                 Returns all data from ISS
  /epochs           Returns list of all Epochs in ISS dataset

  /epochs?"limit=int&offset=int"
                    Returns modified list of Epochs given limit and
                    query parameters
  
  /epochs/<epoch>   Returns state vectors for specified Epoch

  /epochs/<epoch>/speed
                    Returns instantaneous speed for specified Epoch

  /epochs/<epoch>/location
                    Returns the geolocation of the specified Epoch

  /delete-data      Deletes all data from local dataset

  /post-data        Reloads local dataset with data from the web
  
  /comment          Returns a list of all the comments from the data
  
  /header           Returns the header of the dataset
  
  /metadata         Returns the metadata from the dataset
  
  /now              Returns the geolocation of the Epoch closest to 
                    the current time

"""

@app.route('/delete-data', methods=['DELETE'])
def delete_data() -> str:
    """
    Deletes all ISS data from local dictionary object
    """
    global iss_data
    iss_data.clear()
    iss_header.clear()
    iss_metadata.clear()
    return 'Data Cleared \n'

@app.route('/post-data', methods=['POST'])
def update_data() -> str:
    """
    Updates local dictionary object with latest data from NASA website
    """
    request_nasa_data()
    return 'Data Reloaded \n'

@app.route('/comment', methods=['GET'])
def get_comment() -> list:
    """
    Returns list of comments from ISS data
    """
    if iss_data == {}:
        return 'Error: Data cleared. Fetch new data with /post-data \n'
    else:
        iss_comment = []
        for i in iss_data['COMMENT']:
            if (i == None):
                iss_comment.append("")
            else:
                iss_comment.append(i)
        return iss_comment

@app.route('/header', methods=['GET'])
def get_header() -> dict:
    """
    Returns the header of the ISS data
    """
    if iss_header == {}:
        return 'Error: Data cleared. Fetch new data with /post-data \n'
    else:
        return iss_header

@app.route('/metadata', methods=['GET'])
def get_metadata() -> dict:
    """
    Returns the metadata from the ISS data
    """
    if iss_metadata == {}:
        return 'Error: Data cleared. Fetch new data with /post-data \n'
    else:
        return iss_metadata

@app.route('/epochs/<int:epoch>/location', methods=['GET'])
def get_location(epoch):
    """
    Calculates the latitude, longitude, altitude, and geoposition for a 
    specified epoch
    """
    if iss_data == {}:
        return 'Error: Data cleared. Fetch new data with /post-data \n'
    else:
        x = float(iss_data['stateVector'][epoch]['X']['#text'])
        y = float(iss_data['stateVector'][epoch]['Y']['#text'])
        z = float(iss_data['stateVector'][epoch]['Z']['#text'])
        
        # extracting time from epoch format
        epoch_time = epoch_to_datetime(iss_data['stateVector'][epoch]['EPOCH'])
        hrs = epoch_time[2]
        mins = epoch_time[3]        
        MEAN_EARTH_RADIUS = 6371.0 #km

        lat = math.degrees(math.atan2(z, math.sqrt(x**2 + y**2)))                
        lon = math.degrees(math.atan2(y, x)) - ((hrs-12)+(mins/60))*(360/24) + 32
        alt = math.sqrt(x**2 + y**2 + z**2) - MEAN_EARTH_RADIUS
        while (abs(lon) > 180):
            if (lon > 180):
                lon -= 360
            elif (lon < -180):
                lon += 360
            else:
                break
        
        geocoder = Nominatim(user_agent='iss_tracker')
        try:
            geoloc = geocoder.reverse((lat, lon), zoom=25, language='en')
            if (geoloc == None):
                return ('Epoch Entry: {} \nISS Location: the Ocean \n'.format(iss_data['stateVector'][epoch]['EPOCH']))
            else:
                return ('Epoch Entry: {} \nISS Location: {} \n'.format(iss_data['stateVector'][epoch]['EPOCH'], str(geoloc)))
        except Error as e:
            return ('Geopy returned an error - {}'.format(e))


@app.route('/now', methods=['GET'])
def get_current_location() -> str:
    """
    Calculates the latitude, longitude, altitude, and geoposition for the epoch
    closest to the current time
    """
    if iss_data == {}:
        return 'Error: Data cleared. Fetch new data with /post-data \n'
    else:
        closest_epoch = {}
        min_time = 9999
        time_now = time.time()
        for i in iss_data['stateVector']:
            epoch = i['EPOCH']
            time_epoch = time.mktime(time.strptime(epoch[:-5], '%Y-%jT%H:%M:%S'))
            difference = time_now - time_epoch
            if (difference < min_time):
                closest_epoch = i

        x = float(closest_epoch['X']['#text'])
        y = float(closest_epoch['Y']['#text'])
        z = float(closest_epoch['Z']['#text'])
        
        epoch_time = epoch_to_datetime(closest_epoch['EPOCH'])
        hrs = epoch_time[2]
        mins = epoch_time[3]
        MEAN_EARTH_RADIUS = 6371.0 #km

        lat = math.degrees(math.atan2(z, math.sqrt(x**2 + y**2)))
        lon = math.degrees(math.atan2(y, x)) - ((hrs-12)+(mins/60))*(360/24) + 32
        alt = math.sqrt(x**2 + y**2 + z**2) - MEAN_EARTH_RADIUS
        
        while (abs(lon) > 180):
            if (lon > 180):
                lon -= 360
            elif (lon < -180):
                lon += 360
            else:
                break
        
        geocoder = Nominatim(user_agent='iss_tracker')
        try:
            geoloc = geocoder.reverse((lat, lon), zoom=25, language='en')
            if (geoloc == None):
                return ('Current Epoch: {} \nISS Location: the Ocean \n'.format(closest_epoch['EPOCH']))
            else:
                return ('Current Epoch: {} \nISS Location: {}\n'.format(closest_epoch['EPOCH'], str(geoloc)))
        except Error as e:
            return ('Geopy returned an error - {}'.format(e))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
