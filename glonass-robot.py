import requests
import json

class Glonass:
    def __init__(self, login: str, password: str):
        self.url = 'https://d.monitoring.aoglonass.ru/rpc'
        self.buildVersion = self.get_build_version()
        self.token = self.__auth__(login, password)

    # авторизация
    def __auth__(self, login: str, password: str) -> str:
        headers = {
            'Content-Type': 'application/json'
        }
        data = {
            "jsonrpc": "2.0",
            "method": "api1.login",
            "id": 3,
            "buildVersion": self.buildVersion,
            "params": [
                login,
                password,
                False
            ]
        }
        res = requests.post(self.url + '?method=login', headers=headers, json=data)
        try:
            return str(res.json()["result"])
        except:
            try:
                print("Ошибка авторизации: ", res.json()["error"]["message"] )
            except:
                print("Ошибка авторизации")
            quit()
    
    # Получить версию сборки
    def get_build_version(self) -> str:
        url = "https://monitoring.aoglonass.ru/js/app.497c1d8e858bf6de.js"
        headers = {
            "sec-ch-ua-platform": '"Windows"',
            "Referer": "https://monitoring.aoglonass.ru/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36"
        }
        try:
            resp = requests.get(url, headers=headers).text
            index = resp.index("buildVersion")
            return resp[index+31:index+71]
        except:
            return "0a439da7b1a506b1de3f0e12dd8a3110decd54c4"
    
    # получить информацию по ТС
    def get_car_info(self, licence_plate: str):
        headers = {
            'Content-Type': 'application/json'
            }

        data = {
            "jsonrpc": "2.0",
            "method": "api1.vehicle.getPortion",
            "id": 457,
            "buildVersion": self.buildVersion,
            "changeId": 5887263,
            "params": [
                self.token,
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
        response = requests.post(self.url + '?method=vehicle.getPortion', headers=headers, json=data)
        return response
    
    def update_info(self, license_plate: str, vehicle_id: str, eventgenerator_settings_json, comment: str, state: bool) -> None:    
        headers = {
            'Content-Type': 'application/json'
        }
        data = {
            "jsonrpc": "2.0",
            "method": "api1.repo.apply",
            "id": 3561,
            "buildVersion": self.buildVersion,
            "params": [
                self.token,
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
        response = requests.post(self.url, headers=headers, json=data)
        print(license_plate, response.json())

    def activated(self, license_plate: str) -> None:
        try:
            car_info = self.get_car_info(license_plate)
            vehicle_id = car_info.json()["result"]["objects"][0]["id"]
            eventgenerator_settings_json = car_info.json()["result"]["objects"][0]["eventgenerator_settings_json"]
            self.update_info(license_plate, vehicle_id, eventgenerator_settings_json, "", True)
        except:
            print(license_plate, "не удалось активировать")  

    def deactivated(self, license_plate: str, comment: str) -> None:
        try:
            car_info = self.get_car_info(license_plate)
            vehicle_id = car_info.json()["result"]["objects"][0]["id"]
            eventgenerator_settings_json = car_info.json()["result"]["objects"][0]["eventgenerator_settings_json"]
            add_comment = car_info.json()["result"]["objects"][0]["description"]
            if len(add_comment)==0:
                add_comment = comment
            else:
                add_comment += '\n' + comment
            self.update_info(license_plate, vehicle_id, eventgenerator_settings_json, add_comment, False)
        except:
            print(license_plate, "не удалось деактивировать")

if __name__=="__main__":

    cars = Glonass("Login", "Password") 
    
    # активация/деактивация
    cars.deactivated("А000АА000", "Тест")
    cars.activated("А000АА000")
