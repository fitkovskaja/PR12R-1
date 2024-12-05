import requests
import json



def get_location_key_geoposition(api_key, long_lat, language='ru-RU'):

    url = 'http://dataservice.accuweather.com/locations/v1/cities/geoposition/search'
    data = {
        'api_key': api_key,
        'q': ','.join(list(map(str, list(long_lat)))),
        'language': language
    }

    response = requests.get(url, params=data).text
    json_response = json.loads(response)

    return json_response['Key']

def get_location_key_name(api_key, name, language='ru-RU'):

    url = 'http://dataservice.accuweather.com/locations/v1/cities/search'
    data = {
        'apikey': api_key,
        'q': name,
        'language': language,
        'alias': 'Always'
    }

    try:
        response = requests.get(url, params=data).text
        json_response = json.loads(response)

        return json_response[0]['Key'], json_response[0]['LocalizedName']
    except KeyError:
        raise KeyError('Несуществующий город')
    except TypeError:
        raise TypeError('Опаньки! Возможно, превышен лимит запросов')
    except IndexError:
        raise IndexError('Опаньки! Возможно, превышен лимит запросов')


def parse_conditions(current_response, forecast_response):

    current_json_response = json.loads(current_response)[0]
    forecast_json_response = json.loads(forecast_response)[0]

    response = dict()

    response['text_conditions'] = current_json_response['WeatherText']
    response['temperature'] = current_json_response['Temperature']['Metric']['Value']
    response['humidity'] = current_json_response['RelativeHumidity']
    response['wind_speed'] = current_json_response['Wind']['Speed']['Metric']['Value']
    response['precipitation_probability'] = forecast_json_response['PrecipitationProbability']

    return response



def get_conditions_by_key(api_key, location_key, language='ru-RU'):

    url = f'http://dataservice.accuweather.com/currentconditions/v1/{location_key}'
    data = {
        'apikey': api_key,
        'language': language,
        'details': 'true'
    }

    current_response = requests.get(url, params=data).text

    # добываем вероятность осадков
    url = f'http://dataservice.accuweather.com/forecasts/v1/hourly/1hour/{location_key}'
    data = {
        'apikey': api_key,
        'language': language,
        'details': 'true',
        'metric': 'true'
    }

    forecast_response = requests.get(url, params=data).text

    return parse_conditions(current_response, forecast_response)


