from django.shortcuts import render
from datetime import datetime as dt
from django.conf import settings
import requests
from django.http.response import JsonResponse
from .models import Weather

# Create your views here.
def index(request):
    return render(request,"app/index.html")

def request_to_weatherapi(city):
    URL = f"http://api.weatherapi.com/v1/current.json?key={settings.WA_APIKEY}&q={city}"
    res = requests.get(URL)
    res.raise_for_status()
    res_json = res.json()
    return{
        "city": res_json["location"]["name"],
        "description":res_json["current"]["condition"]["text"],
        "icon":f'http:{res_json["current"]["condition"]["icon"]}',
        "temperature":res_json["current"]["temp_c"],
        "updated_date":dt.fromtimestamp(res_json["current"]["last_updated_epoch"]).strftime("%Y-%m-%d %H:%M:%S"),
        "api_response":res.text
    }

def trigger(request):
    city = request.GET.get("city")
    weather_data = request_to_weatherapi(city)
    qset = Weather.objects.filter(city__iexact=city)
    if qset.exists():
        qset.update(**weather_data)
        return JsonResponse({"data": [weather_data],"message": "Updated!"})             
    else:
        Weather.objects.create(**weather_data)
        return JsonResponse({"data": [weather_data],"message": "Created!"})  
    
def query_weather_data(city=None):
    qset = Weather.objects.filter().order_by(
        "-updated_date").distinct()
    if city:
        qset = qset.filter(city__iexact=city)
    return[
        {
            "id":obj.id,
            "city":obj.city,
            "icon":obj.icon,
            "temperature":obj.temperature,
            "description":obj.description,
            "updated_date":obj.updated_date.strftime("%Y-%m-%d %H:%M")
        }
        for obj in qset
    ]
    
def api_data_view(request):
    qs = query_weather_data()
    return JsonResponse(qs,safe=False)