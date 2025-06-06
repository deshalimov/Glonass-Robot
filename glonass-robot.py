import requests
import json

buildVersion = "0a439da7b1a506b1de3f0e12dd8a3110decd54c4"
url = 'https://d.monitoring.aoglonass.ru/rpc'

# Получить версию сборки
def get_build_version():
  url = "https://monitoring.aoglonass.ru/js/app.497c1d8e858bf6de.js"

  headers = {
      "sec-ch-ua-platform": '"Windows"',
      "Referer": "https://monitoring.aoglonass.ru/",
      "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36"
  }


  resp = requests.get(url, headers=headers).text
  index = resp.index("buildVersion")
  return resp[index+31:index+71]

# авторизация
def auth(login, password):
    headers = {
        'Content-Type': 'application/json'
    }
    data = {
        "jsonrpc": "2.0",
        "method": "api1.login",
        "id": 3,
        "buildVersion": buildVersion,
        "params": [
            login,
            password,
            False
        ]
    }

    res = requests.post(url + '?method=login', headers=headers, json=data)

    return str(res.json()["result"])

# получить информацию по ТС
def get_car_info(params, licence_plate):
    headers = {
        'Content-Type': 'application/json'
        }

    data = {
        "jsonrpc": "2.0",
        "method": "api1.vehicle.getPortion",
        "id": 457,
        "buildVersion": buildVersion,
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

    response = requests.post(url + '?method=vehicle.getPortion', headers=headers, json=data)
    return response

def update_info(license_plate, vehicle_id, eventgenerator_settings_json, comment, access_token, state):    

    headers = {
        'Content-Type': 'application/json'
    }

    data = {
        "jsonrpc": "2.0",
        "method": "api1.repo.apply",
        "id": 3561,
        "buildVersion": buildVersion,
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