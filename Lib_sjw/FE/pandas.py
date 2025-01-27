import pandas as pd

#Time Searies
def Split_Datetime(df):
    '''
    year	The year of the datetime.
    month	The month as January=1, December=12.
    day	The days of the datetime.
    hour	The hours of the datetime.
    minute	The minutes of the datetime.
    second	The seconds of the datetime.
    microsecond	The microseconds of the datetime.
    nanosecond	The nanoseconds of the datetime.
    date	Returns numpy array of python datetime.date objects (namely, the date part of Timestamps without timezone information).
    time	Returns numpy array of datetime.time.
    timetz	Returns numpy array of datetime.time also containing timezone information.
    dayofyear	The ordinal day of the year.
    weekofyear	The week ordinal of the year.
    week	The week ordinal of the year.
    dayofweek	The day of the week with Monday=0, Sunday=6.
    weekday	The day of the week with Monday=0, Sunday=6.
    quarter	The quarter of the date.
    freq	Return the frequency object if it is set, otherwise None.
    freqstr	Return the frequency object as a string if it is set, otherwise None.
    is_month_start	Indicates whether the date is the first day of the month.
    is_month_end	Indicates whether the date is the last day of the month.
    is_quarter_start	Indicator for whether the date is the first day of a quarter.
    is_quarter_end	Indicator for whether the date is the last day of a quarter.
    is_year_start	Indicate whether the date is the first day of a year.
    is_year_end	Indicate whether the date is the last day of the year.
    is_leap_year	Boolean indicator if the date belongs to a leap year.
    inferred_freq	Tryies to return a string representing a frequency guess, generated by infer_freq.
    '''
    datetime_instance = pd.DatetimeIndex(df_data['Date Time'])
    df['year']    = datetime_instance.year
    df['month']   = datetime_instance.month
    df['day']     = datetime_instance.day
    df['hour']    = datetime_instance.hour
    df['min']     = datetime_instance.minute
    df['quarter'] = datetime_instance.quarter
    #df['abs_time'] = datetime_instance.astype(np.int64) // 10**9 # 절대시간
    return df

