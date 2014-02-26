# This module handles analytical DB queries and works with Visualization_Tools to generate graphic output 
#For the time being: This has no interface with Database_Tools, which exists just to fill the tables and do a few simple viewing queries.

import sqlite3
import sys
import datetime
import re
import Visualization_Tools as visual_tools
from dateutil import parser

connection = sqlite3.connect('/home/rachelle/Dropbox/Python/DietData/DietLog/Database-Scripts/diet_data.db')

connection.text_factory = str
connection.row_factory = sqlite3.Row

c = connection.cursor()

def display_menu():
	print "Enter CALORIE-DRIVEN to perform analyses concerned primarily with calories consumed."
	print "Enter EXERCISE-DRIVEN for analyses concerned primarily with exercise."
	print "Enter FOOD-DRIVEN for analyses conerning foods, times of consumption, calorie breakdowns, etc."
	#Could do a row of pie charts indicating distribution of daily calories over each meal-time bracket
	#print "Enter FOOD-INFO-DRIVEN for analyses on entered food information: types, calorie densities, portions"
	print "Enter QUIT to exit to interpreter."

	nav_command = raw_input("Enter a command: ")

	if nav_command == 'QUIT':
		quit = raw_input('Enter Y to quit, N to continue working: ')
		if quit == 'Y':
			connection.close()
			sys.exit()
		else:
			nav_command = raw_input('Enter command: ')

	elif nav_command == 'CALORIE-DRIVEN':
		calorie_analysis()

	elif nav_command == 'EXERCISE-DRIVEN':
		exercise_analysis()

	elif nav_command == 'FOOD-DRIVEN':
		food_analysis()

	else:
		print 'Command '+nav_command+' not found.'
		display_menu()

def food_analysis():
	print "View individual date entries or entries over a date range with Database_Tools."
	print "Enter '1' to see how often, or how much of, you ate a particular food over a date range."
		#And then a sub-option of this will be to see during what times of day this food/bev tended to be consumed in
	print "Enter 'BACK' to return to previous menu"

	nav_command = raw_input("Enter analysis number: ")
	master_analysis_list = []

	if nav_command == 'BACK':
		display_menu()

	elif nav_command == '1':
		master_analysis_list = food_sums_and_servings()

def food_sums_and_servings():

	search_food = raw_input("Enter an uncapitalized food or beverage to search for: ")
	date_range = raw_input("Enter the single date or date range to search over: ")

	matching_foods = []

	if ' TO ' in date_range: #Date range given
			date_range = date_range.split(' TO ', 1)
			start = date_range[0]
			end = date_range[1]

			date_foods = list(c.execute('SELECT * FROM food_entries WHERE date BETWEEN ? AND ?', (start, end)))

	else: #Only one date
			date_foods = list(c.execute('SELECT * FROM food_entries WHERE date = ?', (date_range,)))	

	if not date_foods:
			print "Records or foods not found for given data"
			food_analysis()

	else:
			times_consumed = 0
			#Build the list, matching_foods		
			for record in date_foods:
				if search_food.lower() in record[2].lower():
					print record[0]+"  "+record[1]+"  "+record[2]+"  "+str(record[3])
					#     date           time           food name       calories
					matching_foods.append(record)
					times_consumed += 1
			
			print "-------"
			print search_food+" consumed on "+str(times_consumed)+ " occasions"
			print "-------"

			refine_search = raw_input("Refine search by name, time, or servings consumed -- Y/N: ")
	
			if refine_search == 'Y':
				refine_food_analysis(matching_foods, search_food)

			else: food_sums_and_servings()
				

def refine_food_analysis(matching_foods, search_food):
	print "Enter 'NAME' to refine search by additional names for "+search_food
	print "Enter 'TIME' to refine search by times you consumed "+search_food
	print "Enter 'SERVINGS' to determine how many servings of "+search_food+" were eaten"
	print "Enter 'PRINT-LIST' to view the list of foods information currently matching all applied refinement criteria"
	print "Enter 'BACK' to go back to previous menu"
	# You can keep your list in here and keep refining it
				
	refine_command = raw_input("Enter: ")
	
	if refine_command == 'BACK':
		food_sums_and_servings()

	if refine_command == 'NAME':
		matching_foods = refine_food_analysis_by_name(matching_foods, search_food)
		refine_food_analysis(matching_foods, search_food)

	elif refine_command == 'TIME':
		matching_foods = refine_food_analysis_by_time(matching_foods, search_food)
		refine_food_analysis(matching_foods, search_food)

	elif refine_command == 'SERVINGS':
		matching_foods = refine_food_analysis_by_servings(matching_foods, search_food)
		refine_food_analysis(matching_foods, search_food)

	elif refine_command == 'PRINT-LIST':
		for record in matching_foods:
			print record 
		refine_food_analysis(matching_foods, search_food)

	else: 
		print "Command not found"
		refine_food_analysis()

def refine_food_analysis_by_name(matching_foods, search_food):
	print "Enter more phrases to narrow down list of matching food items."
	print "For instance, an initial search for 'milk' might be narrowed with '2%' or 'chocolate'."

	refine_term = raw_input("Enter: ")
	times_consumed = 0
	refined_matching_foods = []

	for record in matching_foods:
		if refine_term.lower() in record[2].lower():
			print record[0]+"  "+record[1]+"  "+record[2]+"  "+str(record[3])
			times_consumed += 1
			refined_matching_foods.append(record)

	print "------"
	print refine_term+" + "+search_food+" consumed "+str(times_consumed)+" times."
	print "------"
					
	return refined_matching_foods

def refine_food_analysis_by_time(matching_foods, search_food):

	print "Enter a time -- morning, afternoon, evening, lunch, etc. to narrow matching rows"
	print "There are no system-enforced time tags, so remember what you call your times!"

	refine_time = raw_input("Enter: ")
	times_consumed = 0

	refined_matching_foods = []

	for record in matching_foods:
		if refine_time.lower() in record[1].lower():
			print record[0]+"  "+record[1]+"  "+record[2]+"  "+str(record[3])
			times_consumed += 1
			refined_matching_foods.append(record)

	print "------"
	print search_food+" eaten in/at time: "+refine_time+" "+str(times_consumed)+" times."
	print "------"

	return refined_matching_foods

def refine_food_analysis_by_servings(matching_foods, search_food):
	print "This functionality requires information for the food's serving size and calories per "
	print "serving."
			
	food_info_list = list(c.execute('SELECT * FROM food_info'))
	#Doing it this not-so-elegant way for now because I haven't figured out how to escape the ?
	#binding whilst using SQL LIKE

	info_with_cals_servs = []
		
	for food in food_info_list:
	#If search_food in the list, and it has serving size and calories/serving information
		if search_food.lower() in food[0].lower() and food[2] != '' and food[3] != '':
			info_with_cals_servs.append(food)

	if not info_with_cals_servs:
		print "No serving size or cals/serving info for "+search_food
		print "Best assumption can be found by computing # of times in food_analysis()"
		food_sums_and_servings()

	else: 
		print "Records available for "+search_food

		for food in info_with_cals_servs:
			print food

		print "Which of these should we use to compute? Give a 0-based row number; if only one, "
		print "just enter '0'"

		row_to_use = raw_input("Enter : ")

		row_to_use = int(row_to_use)

		if not info_with_cals_servs[row_to_use]:
			print "Row not found"
			food_analysis()

		else:
			#Row exists
			serving_size = info_with_cals_servs[row_to_use][3]				
			calories_per_serving = int(info_with_cals_servs[row_to_use][2])

			#How many calories total were eaten of this food?
			total_calories = 0
		
			#Row[3] in matching_foods will have the calories
			for row in matching_foods:
				total_calories += row[3]
				print row

			print "Total calories of item consumed: "+str(total_calories)
							
			computed_servings = total_calories/calories_per_serving
			print "Number of servings/units consumed: "+str(computed_servings)

	return matching_foods

"""
Seemed like it'd be better practice, but it looks like table names may not be parameterized

def select_rows_over_date_range(table, start, end):

	date_rows = list(c.execute('SELECT * FROM ? WHERE date BETWEEN ? AND ?', (table, start, end)))
	return date_rows

def select_single_row_date(table, date):
	date_row = list(c.execute('SELECT * FROM ? WHERE date = ?', (table, date,)))
	return date_row
"""		

def exercise_analysis():
	print "Enter '1' to view exercise for a given date or range of dates."
	print "Enter '2' to tabulate exercise totals for a range of dates."
	print "Enter '3' to manage system list of known exercise types."

	nav_command = raw_input("Enter analysis number: ")

	if nav_command == 'BACK':
		display_menu()

	elif nav_command == '1':
		#Need to get user's range of dates, and then for those simply bring back all matching tuples from table exercise.
		date_range = raw_input("Enter date range as single 'year-mm-dd' or 'year-mm-dd TO year-mm-dd': ")

		if ' TO ' in date_range: #Date range given
			date_range = date_range.split(' TO ', 1)
			start = date_range[0]
			end = date_range[1]

			range_exercise = list(c.execute('SELECT * FROM exercise WHERE date BETWEEN ? AND ?', (start, end)))
		
		else: #Only one date
			range_exercise = list(c.execute('SELECT * FROM exercise WHERE date = ?', (date_range,)))

		if not range_exercise:
			print "Records not found for given range"
			exercise_analysis()

		else:
			for record in range_exercise:
				print record[0]+"  "+record[1]

	elif nav_command == '2':
		date_range = raw_input("Enter date range as single 'year-mm-dd' or 'year-mm-dd TO year-mm-dd': ")

		if ' TO ' in date_range: #Date range given
			date_range = date_range.split(' TO ', 1)
			start = date_range[0]
			end = date_range[1]

			range_exercise = list(c.execute('SELECT * FROM exercise WHERE date BETWEEN ? AND ?', (start, end)))
		
		else: #Only one date
			range_exercise = list(c.execute('SELECT * FROM exercise WHERE date = ?', (date_range,)))

		if not range_exercise:
			print "Records not found for given range"
			exercise_analysis()

		else:
			#Now, rather than dumping this out to screen, we're going to group things by exercise rather than date
			#Column in exercise_info with conjugated verb forms is not needed -- just use the base form of the 
			#verb, along with an enforced input format. Format: <time spent as decimal hours>, <exercise verb base form>

			#In Database_Tools, will need to do a check of the tag list for anything inputted in the exercise field,
			#exactly as is done for food_entries and food_info
			exercise_totals_list = []

			exercise_tag_list = list(c.execute('SELECT * FROM exercise_info'))

			if not exercise_tag_list:
				print "No exercise tags to analyze data with; please go enter some with option 3"
				exercise_analysis()

			else:
				for record in range_exercise:
					#record[0] contains the date, record[1] the exercise string
					if record[1].lower() == "none": continue #If no exercise for the day, skip

					#Handle multiple exercise types for a single day, if need be
					elif ", " in record[1]:
						exercises = record[1].split(', ')
						for exercise in exercises:
							exercise_totals_list.append(exercise)
					
					#Single exercise listed for the day						
					else: exercise_totals_list.append(record[1])
	
		#Now that we have a list with all exercises included, we need to calculate times
		#spent doing each activity and display them as a group			
		#We are now enforcing a strict format, so can easily pull times and dates
		final_counts = []
		raw_finals_counts = []

		for tag in exercise_tag_list: #Categorize by tag
			duration = 0.0
			times_count = 0

			for row in exercise_totals_list:

				if tag[0] in row:
					if contains_digits(row): #If row contains numbers, it's an hourly activity
						#We should split and take the first item off to get our float number
						numbers = row.split(" ") #Split around space
						numbers = numbers[0]
						duration += float(numbers)
					else: #It's an activity counted in times done, rather than in terms of duration
						times_count += 1

			if duration == 0 and times_count == 0: continue #If no time spent, don't add anything to final_counts

			if duration != 0 and times_count == 0: #If we have a duration
				activity = tag[0]
				final_counts.append("Total hours spent on activity: "+tag[0]+" = "+str(duration))
				raw_finals_counts.append([tag[0], duration])

			if duration == 0 and times_count != 0: #If we have a counted activity
				activity = tag[0]
				final_counts.append("Activity: "+tag[0]+" done "+str(times_count)+" times.")
				raw_finals_counts.append([tag[0], times_count])
		
		for item in final_counts:
			print item

		to_pie_chart = raw_input("Enter 'Y' to visualize breakdown as pie chart, 'N' to return to menu: ")

		if to_pie_chart == 'Y': visual_tools.exercise_pie_chart(raw_finals_counts, start, end)
		
		else: display_menu()
				
		

	elif nav_command == '3':
		print "To view current contents of known exercise-type system list, enter '1'."
		print "To add exercise types to the system list, enter '2'."
		print "Enter 'BACK' to return to exercise analysis menu."

		nav_number = raw_input("Enter command: ")

		if nav_number == 'BACK':
			exercise_analysis()
		elif nav_number == '1':
			#System tags exist as entries for the single column exercise_name in table exercise_info
			exercise_tag_list = list(c.execute('SELECT * FROM exercise_info'))

			if not exercise_tag_list: 
				print "No system tags for exercise -- input some?"

			else: 
				for tag in exercise_tag_list: print tag[0]+" "+tag[1]

		elif nav_number == '2':
			while True:
				#Add a system tag; an ugly system, but I'm entering 3 forms of the exercise verb; base, past, gerund
				#Also, for my purposes, entering "work" to be an indicator that I commuted by bike/foot
				tag_to_enter = raw_input("Enter an exercise tag as possible verb form: ")
				exercise_group = raw_input("Enter the exercise base verb form: ")				
				c.execute('INSERT INTO exercise_info VALUES (?, ?)', (tag_to_enter, exercise_group))
	
				continue_adding = raw_input('Enter Y to keep adding tags, N to stop: ' )

				if continue_adding.strip() == 'N':
					connection.commit()
					break
		

		else: 
			print "Command not found"
			exercise_analysis()


	display_menu()		


def contains_digits(text):
	_digits = re.compile('\d')
	_decimaldigits_nolead = re.compile('.\d+')
	_decimaldigits = re.compile('\d+.\d+')
	if _digits.search(text) or _decimaldigits_nolead.search(text) or _decimaldigits.search(text):
		return True

def calorie_analysis():
	print "Enter the number of the analysis to query on and produce listed, visualization-ready data: "
	print "1. View total calories over a range of dates. For viewing entries as text in terminal, use Database_Tools.view_dates()"
	print "2. Sum up total calorie count for a range of dates."
	print "3. Calculate a single BMR and visually compare it a date range of calories consumed."
	print "4. Calculate changing BMR/daily burn estimations to reflect weight/activity/age changes over a long date range."
	
	nav_command = raw_input("Enter analysis number: ")

	if nav_command == 'BACK':
		display_menu()

	elif nav_command == '1':
		#Need to get user's range of dates, and then for those simply bring back all matching tuples from table daily_totals.
		date_range = raw_input("Enter date range as 'year-mm-dd TO year-mm-dd': ")
		date_range = date_range.split(' TO ', 1)
		start = date_range[0]
		end = date_range[1]

		range_calories = list(c.execute('SELECT * FROM daily_totals WHERE date BETWEEN ? AND ?', (start, end)))

		if not range_calories:
			#If it should happen that the end is chronologically before start, query will fail and list will be empty
			print "Records not found for given range."
			calorie_analysis()

		else:
			for record in range_calories:
				print record[0]+"  "+str(record[1])

		pipe_to_visuals = raw_input("Plot information? -- Y or N: ")

		if pipe_to_visuals == 'Y': visual_tools.calories_over_range(range_calories)

		else: calorie_analysis()

	elif nav_command == '2':
		#Fetch range of dates, just as done above, and sum up the calories column for all dates.
		date_range = raw_input("Enter date range as 'year-mm-dd TO year-mm-dd': ")
		date_range = date_range.split(' TO ', 1)
		start = date_range[0]
		end = date_range[1]

		range_calories = list(c.execute('SELECT * FROM daily_totals WHERE date BETWEEN ? AND ?', (start, end)))

		if not range_calories:
			print "Records not found for given range."
			calorie_analysis()
		else:
			total_calories = 0
			total_days = len(range_calories)
			missing_days = 0 #Keep count of days for which there were no records, and remove them from average computation

			for record in range_calories:
				if record[1] == 0: #If no record
					missing_days += 1
				total_calories += record[1] #Sum up all the calories over given period 

			total_days -= missing_days #Subtract missing days from total days

			print "Total calories consumed over range "+start+" to "+end+": "+str(total_calories)
			print "Total days missing records: "+str(missing_days)
			print "Average calories per day: "+str(total_calories/total_days)

	elif nav_command == '3':
		#Give user information about the BMR formula, then get operands. Compute. Then use Harris Benedict equation to compute
		#an approximation for daily expenditures that include physical activity.
		#This number will be used in visualization as line against which calorie intake will be compared. 
		#This comparison can be used to generate predictions on calories lost/gained/maintained

		print "------------------"
		print "We'll first collect gender, height, weight, and age information to compute your base metabolic rate, or BMR."
		print "Your BMR represents the estimated number of calories your body would burn in maintaining itself if you were to "
		print "lay motionless for an entire 24 hour period."
		print "------------------"

		gender = raw_input("Would your physiology be best categorized as MALE or FEMALE?: ")
		height = raw_input("In inches, how tall are you: ")
		height = float(height)
		weight = raw_input("In pounds, how much do you weigh: ")
		weight = float(weight)
		age = raw_input("Age: ")
		age = float(age)

		if gender == 'MALE':
			 estimated_BMR = 66+((6.23*weight)+(12.7*height)-( 6.8*age))
		elif gender == 'FEMALE':
			estimated_BMR = 655+((4.35*weight)+(4.7*height)-(4.7*age))
		else:
			print "Gotta fit the binary. Try again."
			calorie_analysis()
		
		print "------------------"
		print "Estimated BMR: "+str(estimated_BMR)
		print "------------------"

		print "Now consider your level of activity. If you are a bed-desk-car type person with basically no physical activity, "
		print "enter SEDENTARY. If you are lightly active, with perhaps a brisk walk 1-3 times per week, enter LIGHT."
		print "If you are get your pulse up with biking, light jogging, or other not-overly-intense but decent activities, enter "
		print "MODERATE. If you are serious about exercise and work out hard most days of the week, input INTENSE. Finally, if you "
		print "are an athlete, in marathon training, or workout in addition to having a physical job, input MAXIMUM." 

		print "------------------"

		activity_level = raw_input("Enter activity level: ")

		#Multiply BMR by a scalar associated with each activity level to get estimated daily calorie burn
		
		if activity_level == 'SEDENTARY':
			estimated_daily_burn = estimated_BMR*1.2
		elif activity_level == 'LIGHT':
			estimated_daily_burn = estimated_BMR*1.375
		elif activity_level == 'MODERATE':
			estimated_daily_burn = estimated_BMR*1.55
		elif activity_level == 'INTENSE':
			estimated_daily_burn = estimated_BMR*1.725
		elif activity_level == 'MAXIMUM':
			estimated_daily_burn = estimated_BMR*1.9
		else:
			print "Activity level description not found. Use the indicated descriptors."			

		print "Estimated daily burn: "+str(estimated_daily_burn)
		print "------------------"

		pipe_to_visuals = raw_input("Prepare output with imposed daily expense rate for visual comparison? Y or N: ")
	
		if pipe_to_visuals == 'Y': 
			#Fetch range of dates, just as done above, and sum up the calories column for all dates.
			#MOVE ALL THIS TO A SEPERATE HELPER FUNCTION THAT RETURNS DAILY_TOTALS OVER A RANGE
			date_range = raw_input("Enter date range as 'year-mm-dd TO year-mm-dd': ")
			date_range = date_range.split(' TO ', 1)
			start = date_range[0]
			end = date_range[1]

			range_calories = list(c.execute('SELECT * FROM daily_totals WHERE date BETWEEN ? AND ?', (start, end)))

			if not range_calories:
				print "Records not found for given range."
				calorie_analysis()

			visual_tools.calories_over_range(range_calories)

		else: calorie_analysis()
		

	else:
		print 'Command '+nav_command+' not found.'
		calorie_analysis()

#####Run script

display_menu()
