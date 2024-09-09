from .models import TravelTime

def get_travel_time(from_zone, to_zone):
    try:
        travel_time = TravelTime.objects.get(from_zone=from_zone, to_zone=to_zone)
        return travel_time.time_minutes
    except TravelTime.DoesNotExist:
        return None