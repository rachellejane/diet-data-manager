import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import datetime
from matplotlib.dates import MonthLocator, DateFormatter, DayLocator

plt.ioff()

def exercise_pie_chart(raw_finals_counts, start, end):

	labels = []
	fracs = []
	countable_items = []	

	for datapoint in raw_finals_counts:
		#datapoint[0] contains the name, datapoint[1] the total duration or times done.
		#If datapoint[1] is an int, then it's a counted activity (like bike commutes)
		if isinstance(datapoint[1], int):
			countable_items.append(datapoint)
			#Need to have this display as a caption
		else: #Datapoint represents something that should go to the pie chart
			labels.append(datapoint[0]+"\n"+str(datapoint[1])+" hours")
			fracs.append(datapoint[1])
	
	# make a square figure and axes
	plt.figure(1, figsize=(6,6))

	plt.pie(fracs, labels=labels, autopct='%1.1f%%', shadow=True)
                # The default startangle is 0, which would start
                # the Frogs slice on the x-axis.  With startangle=90,
                # everything is rotated counter-clockwise by 90 degrees,
                # so the plotting starts on the positive y-axis.

	plt.title('Exercise breakdown for date range: \n'+start+" to "+end, bbox={'facecolor':'0.8', 'pad':5})

	plt.rcParams['text.color'] = 'r'
	plt.rcParams['lines.linewidth'] = 2
	plt.rcParams['font.family'] = 'monospace'
	plt.rcParams['font.weight'] = 'bold'
	
	plt.show()

def calories_over_range(dates_calories_sqlite_row, bmr):

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

	bmr_values = []

	if bmr != None:
		#Fill bmr values list
		for each in datetimes_list:
			bmr_values.append(bmr)		


	plt.gca().xaxis.set_major_formatter(DateFormatter(date_format))
	plt.gca().xaxis.set_major_locator(date_range)
	
	calories_list = np.array(calories_list)

	calories_list_ma = np.ma.masked_where(calories_list == 0, calories_list) #Apply numpy mask to calories_list, masking out 0s as empt
	
	plt.plot(datetimes_list, calories_list_ma, marker = 'x', color = 'r', ls = '-')

	plt.gcf().autofmt_xdate()

	#Draw BMR/Estimated Daily Burn line
	plt.plot(datetimes_list, bmr_values,  color = 'b', ls = '-')

	plt.title("Calories Over Date Range: "+str(start_date)+" to "+str(end_date))
    
	plt.show()

