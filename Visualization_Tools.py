import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import datetime
from matplotlib.dates import MonthLocator, DateFormatter, DayLocator

plt.ioff()

def calories_over_range(dates_calories_sqlite_row):

	calories_datetimes_list = []
	calories_list = []
	datetimes_list = []

	for day in dates_calories_sqlite_row:
		#Get all dates in the list converted to datetime objects	
		day = list(day) #When data is brought in as SQLite Row, have to convert tuple to list

		day[0] = day[0].split('-', 2)

		datetime_day = datetime.date(int(day[0][0]), int(day[0][1]), int(day[0][2])) #Make datetime objects (year, mm, dd)

		#Because we can't just change day[0] to a datetime object in place, we assemble a new list
		calories_datetimes_list.append([datetime_day, day[1]])

		#And then we'll keep two separate ones, too, just for processing ease later on		
		calories_list.append(day[1])
		datetimes_list.append(datetime_day)

	start_date = datetimes_list[0]
	end_date = datetimes_list[len(datetimes_list) -1]

	print "Start date: "+str(start_date)
	print "End date: "+str(end_date)

	#Find smallest and largest calorie counts for ymin and ymax
	ymin = min(calories_list)
	ymax = max(calories_list)

	#Find earliest and most recent dates for xmin and xmax
	xmin = min(datetimes_list)
	xmax = max(datetimes_list)

	points_count = len(datetimes_list) #Get number of points

	#plt.axis([xmin, xmax, ymin, ymax]) It actually looks better when matplotlib handles this itself

	if xmin.year == xmax.year and points_count < 10: #If years the same, no need to repeatedly display the year on each date
		date_format = '%m-%d'
		date_range = DayLocator(bymonthday=None, interval=1, tz=None)
	elif xmin.year == xmax.year and points_count >= 10: #Dont' display same year and don't clutter up x-axis w/too many dates
		date_format = '%m-%d'
		date_range = DayLocator(bymonthday=None, interval=2, tz=None) #Display every other day if >10 dates
	#elif: define more elif conditions for more situations as they arise
	else:
		date_format = '%Y-%m-%d'
		
	#Get month range from the date -- come back later and set this to run on a conditional, depending on length of date range
	#months    = MonthLocator(range(0, 3), bymonthday=1, interval=1)
	#monthsFmt = DateFormatter("%b '%y")

	plt.gca().xaxis.set_major_formatter(DateFormatter(date_format))
	plt.gca().xaxis.set_major_locator(date_range)
	
	calories_list = np.array(calories_list)

	calories_list_ma = np.ma.masked_where(calories_list == 0, calories_list) #Apply numpy mask to calories_list, masking out 0s as empt
	
	plt.plot(datetimes_list, calories_list_ma, marker = 'x', color = 'r', ls = '-')

	plt.gcf().autofmt_xdate()

	plt.title("Calories Over Date Range: "+str(start_date)+" to "+str(end_date))
    
	plt.show()

