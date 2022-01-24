from django.core.validators import RegexValidator


PHONE_NUMBER_REGEX = RegexValidator(regex=r'^[0-9]{10}$', message="Phone number must have total 10 numbers.")