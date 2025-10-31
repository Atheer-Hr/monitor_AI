# utils.py
import hashlib

def classify_severity(note):
    note = note.lower()
    if any(word in note for word in ['إغماء', 'نزيف', 'طارئة', 'إسعاف']):
        return 'طارئة'
    elif any(word in note for word in ['صداع', 'تعب', 'انعزال', 'قلق']):
        return 'تحتاج متابعة'
    else:
        return 'عادية'

        
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

