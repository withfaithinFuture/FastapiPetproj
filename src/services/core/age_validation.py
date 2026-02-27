import datetime as dt
from dateutil.relativedelta import relativedelta
from src.services.core.exceptions import AgeMinorError, FutureDateError


def validate_age(bd_date: dt.date) -> None:
    today_date = dt.date.today()
    age = relativedelta(today_date, bd_date).years

    if 0 < age < 18:
        raise AgeMinorError(bd_date)

    elif age < 0:
        raise FutureDateError(bd_date)