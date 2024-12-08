from flask import Flask, render_template, request
from dotenv import load_dotenv
import os
from api import get_weather, get_location_key, check_bad_weather, parse_needed_values, ForecastError, LocationSearchError, WeatherValuesError


load_dotenv()

app = Flask(__name__)
API_KEY = os.getenv("API_KEY")  # Исправлено на правильное получение ключа

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        start = request.form.get("start")
        end = request.form.get("end")

        try:
            start_key = get_location_key(start)
            end_key = get_location_key(end)

            start_weather = get_weather(start_key)
            end_weather = get_weather(end_key)
            
            start_temperature, start_wind_speed, start_precipitation = parse_needed_values(start_weather)
            end_temperature, end_wind_speed, end_precipitation = parse_needed_values(end_weather)

            start_status = check_bad_weather(start_temperature, start_wind_speed, start_precipitation)
            end_status = check_bad_weather(end_temperature, end_wind_speed, end_precipitation)

            if start_status:
                start_status_message = 'Хорошая погода, вперед!'
            else:
                start_status_message = 'Ой-ей! С погодой что-то не так. Лучше отложите путешествие.'

            if end_status:
                end_status_message = 'Хорошая погода, вперед!'
            else:
                end_status_message = 'Ой-ей! С погодой что-то не так. Лучше отложите путешествие.'

            return render_template("result.html", 
                                   start_status=start_status_message,
                                   end_status=end_status_message,
                                   start_temperature=start_temperature,
                                   start_wind_speed=start_wind_speed,
                                   start_precipitation=start_precipitation,
                                   end_temperature=end_temperature,
                                   end_wind_speed=end_wind_speed,
                                   end_precipitation=end_precipitation)
        
        except LocationSearchError as e:
            return render_template("error.html", message=str(e))
        
        except ForecastError as e:
            return render_template("error.html", message=str(e))

        except WeatherValuesError as e:
            return render_template("error.html", message="Не удалось получить данные о погоде. Проверьте корректность введенных данных.")

        except Exception as e:
            return render_template("error.html", message="Произошла неизвестная ошибка.")

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)