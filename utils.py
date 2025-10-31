import hashlib

def classify_severity(note):
    """
    يصنف شدة الملاحظة بناءً على كلمات مفتاحية.
    """
    note = note.lower()
    if any(word in note for word in ['إغماء', 'نزيف', 'طارئة', 'إسعاف']):
        return 'طارئة'
    elif any(word in note for word in ['صداع', 'تعب', 'انعزال', 'قلق']):
        return 'تحتاج متابعة'
    else:
        return 'عادية'

def hash_password(password):
    """
    يُحوّل كلمة المرور إلى تمثيل مشفر باستخدام SHA-256.
    """
    return hashlib.sha256(password.encode()).hexdigest()
