from datetime import datetime

class DateConverter:
    regex = r'\d{4}-\d{2}-\d{2}'  # Matches YYYY-MM-DD

    def to_python(self, value):
        # Converts the string from the URL into a date object
        return datetime.strptime(value, '%Y-%m-%d').date()

    def to_url(self, value):
        # Converts the date object back into a string for reverse()
        return value.strftime('%Y-%m-%d')
