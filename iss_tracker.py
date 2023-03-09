from flask import Flask, request
import requests
import xmltodict
import math

app = Flask(__name__)
global iss_data

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
  
  /delete-data      Deletes all data from local dataset
  /post-data        Reloads local dataset with data from the web\n
"""

@app.route('/delete-data', methods=['DELETE'])
def delete_data() -> str:
    """
    Deletes all ISS data from local dictionary object
    """
    global iss_data
    iss_data.clear()
    return 'Data Cleared \n'

@app.route('/post-data', methods=['POST'])
def update_data() -> str:
    """
    Updates local dictionary object with latest data from NASA website
    """
    request_nasa_data()
    return 'Data Reloaded \n'

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
