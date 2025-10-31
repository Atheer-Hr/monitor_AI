from datetime import time

def check_status(arrival_time):
    threshold = time(7, 30)
    return "متأخر" if arrival_time > threshold else "في الوقت"

def generate_alert(student_name, arrival_time):
    return f"🔔 الطالب {student_name} وصل متأخرًا في {arrival_time.strftime('%H:%M')}. يرجى المتابعة."
