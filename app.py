import location
import model
from flask import Flask, request, render_template
from markupsafe import Markup

API_KEY = "dnltQ6zP5xKe04QUFtm1lUOUeLLgkA3E"
app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        starting_city = request.form.get("starting_city")
        end_city = request.form.get("end_city")
        mode = request.form.get("mode")

        try:
            # Ключи и имена городов
            starting_city_key, starting_city_name = location.get_location_key_name(API_KEY, starting_city)
            end_city_key, end_city_name = location.get_location_key_name(API_KEY, end_city)
        except Exception as e:
            # Обработка ошибок
            return render_template("error.html", error=str(e))

        try:
            # Данные о погоде для городов
            starting_weather = location.get_conditions_by_key(API_KEY, starting_city_key)
            end_weather = location.get_conditions_by_key(API_KEY, end_city_key)
        except Exception as e:
            # Обработка ошибок
            return render_template("error.html", error="Ошибка при получени данных о погоде" + str(e))

        # Приведим данные к нужному виду
        starting_weather_formated = model.weather_format(starting_weather)
        end_weather_formated = model.weather_format(end_weather)

        # Оценка погодных условий
        weather_states = {
            True: 'Погодные условия благоприятны для путешествий',
            False: 'Погодные условия сомнительны, длительное нахождение на улице может быть некомфортным',
        }

        starting_weather_evaluation, starting_weather_reasons = model.check_weather(starting_weather, mode)
        end_weather_evaluation, end_weather_reasons = model.check_weather(end_weather, mode)

        starting_reasons_formatted = ''
        end_reasons_formatted = ''

        key_features = {
            'temperature': 'Температура',
            'humidity': 'Влажность',
            'wind_speed': 'Скорость ветра',
            'precipitation_probability': 'Вероятность осадков'
        }

        # Несоответствие выбранному режиму
        if len(starting_weather_reasons) > 0:
            starting_reasons_formatted = ('Следующие параметры могут сделать пребывание на улице некомфортным: ' +
                                       ', '.join(map(lambda x: key_features[x], starting_weather_reasons)))
        if len(end_weather_reasons) > 0:
            end_reasons_formatted = ('Следующие параметры могут сделать пребывание на улице некомфортным: ' +
                                     ', '.join(map(lambda x: key_features[x], end_weather_reasons)))

        # Форматируем для отображения на странице
        return render_template("result.html", 
                               starting_city=starting_city_name, 
                               end_city=end_city_name,

                               starting_weather=Markup(weather_states[starting_weather_evaluation] + '<br/>' +  starting_reasons_formatted),
                               end_weather=Markup(weather_states[end_weather_evaluation] + '<br/>' + end_reasons_formatted),

                               starting_weather_list=starting_weather_formated, 
                               end_weather_list=end_weather_formated)
    return render_template("index.html")

@app.route("/result")
def result():
    return render_template("result.html")

if __name__ == "__main__":
    app.run()
