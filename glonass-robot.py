import requests
import json

# авторизация
def auth(login, password):
    url = 'https://monitoring.aoglonass.ru/rpc?method=login'
    headers = {
        'Content-Type': 'application/json'
    }
    data = {
        "jsonrpc": "2.0",
        "method": "api1.login",
        "id": 3,
        "buildVersion": "5c2f6373d13417f0dff6a1e572c2009734450c7f",
        "params": [
            login,
            password,
            False
        ]
    }

    res = requests.post(url, headers=headers, json=data)

    return str(res.json()["result"])

# получить информацию по ТС
def get_car_info(params, licence_plate):
    url = 'https://d.monitoring.aoglonass.ru/rpc?method=vehicle.getPortion'
    headers = {
        'Content-Type': 'application/json'
        }

    data = {
        "jsonrpc": "2.0",
        "method": "api1.vehicle.getPortion",
        "id": 457,
        "buildVersion": "5c2f6373d13417f0dff6a1e572c2009734450c7f",
        "changeId": 5887263,
        "params": [
            params,
            {
                "offset": 0,
                "filter": {
                    "operator": "or",
                    "conditions": [
                        {
                            "condition": "contain",
                            "columns": [
                                "name"
                            ],
                            "value": licence_plate
                        }
                    ]
                },
                "with_fence": False
            },
            {
                "recursive": True,
                "groups": [
                    "569ee595-ccd0-463f-a2b1-cd9992311e42"
                ]
            }
        ]
    }

    response = requests.post(url, headers=headers, json=data)
    return response

def update_info(license_plate, vehicle_id, eventgenerator_settings_json, comment, access_token, state):    

    url = 'https://d.monitoring.aoglonass.ru/rpc'
    headers = {
        'Content-Type': 'application/json',
        'Cookie': 'MonitoringSessionID=ffffffff0945d34e45525d5f4f58455e445a4a423660'
    }

    data = {
        "jsonrpc": "2.0",
        "method": "api1.repo.apply",
        "id": 3561,
        "buildVersion": "5c2f6373d13417f0dff6a1e572c2009734450c7f",
        "params": [
            access_token,
            {
                "vehicle": {
                    vehicle_id: {
                        "op": "edit",
                        "fields": {
                            "description": comment,
                            "enabled": state,
                            "parameters_json": "{\"sensorTriggers\":[]}",
                            "eventgenerator_settings_json": eventgenerator_settings_json
                        }
                    }
                }
            }
        ]
    }

    response = requests.post(url, headers=headers, json=data)

    print(license_plate, response.json())
    #return response

def activated(license_plate, access_token):
    try:
        car_info = get_car_info(access_token, license_plate)
        vehicle_id = car_info.json()["result"]["objects"][0]["id"]
        eventgenerator_settings_json = car_info.json()["result"]["objects"][0]["eventgenerator_settings_json"]
        update_info(license_plate, vehicle_id, eventgenerator_settings_json, "", access_token, True)
    except:
        print(license_plate, "не удалось активировать")

def deactivated(license_plate, comment, access_token):
    try:
        car_info = get_car_info(access_token, license_plate)
        vehicle_id = car_info.json()["result"]["objects"][0]["id"]
        eventgenerator_settings_json = car_info.json()["result"]["objects"][0]["eventgenerator_settings_json"]
        update_info(license_plate, vehicle_id, eventgenerator_settings_json, comment, access_token, False)
    except:
        print(license_plate, "не удалось деактивировать")   

def add_comment_deactivated(license_plate, comment, access_token):
    try:
        car_info = get_car_info(access_token, license_plate)
        vehicle_id = car_info.json()["result"]["objects"][0]["id"]
        eventgenerator_settings_json = car_info.json()["result"]["objects"][0]["eventgenerator_settings_json"]
        add_comment = car_info.json()["result"]["objects"][0]["description"]
        if len(add_comment)==0:
            add_comment = comment
        else:
            add_comment += '\n' + comment
        update_info(license_plate, vehicle_id, eventgenerator_settings_json, add_comment, access_token, False)
    except:
        print(license_plate, "не удалось деактивировать")

if __name__=="__main__":
    # получить токен
    access_token = auth("Smartseeds", "123Asd") 

    # активация/деактивация
    #deactivated("К459РО126", "тест", access_token)
    #activated("К459РО126", access_token)
    add_comment_deactivated("А002ХУ93", "Приостановлен по просьбе ОРИДС из письма 03.06.2025", access_token)
