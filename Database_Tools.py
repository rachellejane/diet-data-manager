import sqlite3
import sys
import datetime
from dateutil import parser

connection = sqlite3.connect('/home/rachelle/Dropbox/Python/DietData/DietLog/Database-Scripts/diet_data.db')

connection.text_factory = str
connection.row_factory = sqlite3.Row

c = connection.cursor()

def display_menu():

	print "Enter 'NEW' to add a new day's worth of data."
	print "Enter 'ANALYZE' to pull chosen data and run analytics"
	#print "Enter 'EDIT' to edit an entry"
	#print "Enter 'HELP' to display manual page." -- move this to driving class
	print "Enter 'QUIT' to exit to interpreter"

	nav_command = raw_input('Enter Command: ')

	if nav_command == 'NEW':
		add_new_date()
	elif nav_command == 'ANALYZE':
		analyze()
	elif nav_command == 'HELP':
		print "This functionality not yet built"
		#display_help_page()
	elif nav_command == 'QUIT':
		quit = raw_input('Enter Y to quit, N to continue working: ')
		if quit == 'Y':
			connection.close()
			sys.exit()
		else:
			nav_command = raw_input('Enter command: ')
	else:
		print 'Command '+nav_command+' not found.'
		display_menu()

def analyze():
	#Just set up an easy way to build SQLite queries for the time being
	#Wishlist for analyze: a command called 'IDEAS' that tosses up randomized analysis possibilities	
	print "Analysis Tools: "
	print "Enter 'VIEW-DATES' to view entries for one or more days"
	print "Enter 'VIEW-FOOD-INFO' to view food information by name, type, or calorie density"
	print "Enter 'BACK' to return to menu"

	nav_command = raw_input('Enter Command: ')

	if nav_command == 'VIEW-DATES':
		view_dates()
	elif nav_command == 'VIEW-FOOD-INFO':
		view_foods_info()
	elif nav_command == 'BACK':
		display_menu()
	else:
		print 'Command '+nav_command+' not found.'
		analyze()

def view_foods_info():
	#View food entries by name and other attributes (like calorie count, type, etc.)
	print "Enter 'NAME' to view by name, 'TYPE' to view by type, 'CALORIES' to view by calories/serving, or 'BACK'"
	
	info_command = raw_input('Enter Command: ')

	if info_command == 'BACK':
		analyze()

	elif info_command == 'NAME':
		food_name = raw_input('Enter food name: ')
		food_info_list = list(c.execute('SELECT * FROM food_info WHERE name = ? COLLATE NOCASE', (food_name,)))

		if not food_info_list:
			print "No information found for: "+food_name
			view_foods_info()

		else:
			for item in food_info_list:
				print "\n"
				print "Food: "+item[0]
				print "Type(s): "+item[1]
				print "Calories per serving: "+str(item[2])
				print "Serving size: "+item[3]+"\n"

		view_foods_info()

	elif info_command == 'TYPE':
		type_entry = raw_input('Enter food type/attribute: ')

		food_info_list = list(c.execute('SELECT * FROM food_info'))

		results_list = []

		for result in food_info_list:
			if result[1].find(type_entry) != -1:
				results_list.append(result)

		if not results_list:
			print "No foods found with type/attribute: "+type_entry
			view_foods_info()
		
		else:
			print "Recorded foods of type: "+type_entry+"\n"
			for result in results_list:
				print "Food name: "+result[0]+" // Food type(s): "+result[1]
				if not result[2]: continue
				else: print "     Calories/serving: "+str(result[2])
				if not result[3]: continue
				else: print "     Serving size: "+result[3]
							
			 
		print "\n"
		view_foods_info()

	elif info_command == 'CALORIES':
		calories = raw_input("Enter a number as =X, range of numbers as 'X-Y', or <X / >X. Resolution is 5 calories.: ")

		if '-' in calories:
			
			calories = calories.split('-', 1)
			start = calories[0]
			end = calories[1]

			calories_list = list(c.execute('SELECT * FROM food_info WHERE calories_per_serving BETWEEN ? AND ? AND 				calories_per_serving IS NOT NULL', (start, end)))

			if not calories_list:
				print "No foods found in range."
				view_foods_info()

			else:
				for result in calories_list:
					if not result[2]: continue
					else: 
						print "     Calories/serving: "+str(result[2])
						print "Food name: "+result[0]+" // Food type(s): "+result[1]	

			view_foods_info()

		elif '<' in calories:
			
			calories = calories.translate(None, '<')
			
			calories_list = list(c.execute('SELECT * FROM food_info WHERE calories_per_serving <= ? AND calories_per_serving IS 				NOT NULL', (calories,)))

			if not calories_list:
				print "No foods found less than "+calories+" calories."
				view_foods_info()

			else:
				for result in calories_list:
					if not result[2]: continue
					else:
						print "Food name: "+result[0]+" // Food type(s): "+result[1]
						print "     Calories/serving: "+str(result[2])
					if not result[3]: continue
					else: print "     Serving size: "+result[3]
				view_foods_info()
						

		elif '>' in calories:
			
			calories = calories.translate(None, '>')
			
			calories_list = list(c.execute('SELECT * FROM food_info WHERE calories_per_serving >= ? AND calories_per_serving IS 				NOT NULL', (calories,)))

			if not calories_list:
				print "No foods found greater than "+calories+" calories."
				view_foods_info()

			else:
				for result in calories_list:
					if not result[2]: continue
					else: 
						print "Food name: "+result[0]+" // Food type(s): "+result[1]
						print "     Calories/serving: "+str(result[2])
					if not result[3]: continue
					else: print "     Serving size: "+result[3]	
				view_foods_info()
		
		elif '=' in calories:
			
			calories = calories.translate(None, '=')
			
			calories_list = list(c.execute('SELECT * FROM food_info WHERE calories_per_serving = ? AND calories_per_serving IS 				NOT NULL', (calories,)))

			if not calories_list:
				print "No foods found equal to "+calories+" calories."
				view_foods_info()

			else:
				for result in calories_list:
					if not result[2]: continue
					else: 
						print "Food name: "+result[0]+" // Food type(s): "+result[1]
						print "     Calories/serving: "+str(result[2])
					if not result[3]: continue
					else: print "     Serving size: "+result[3]	
				view_foods_info()			
	else:
		print "Command not found"
		view_foods_info()
		

def view_dates():
	#Display rows for one or more dates
	print "Enter single year-mm-dd date or year-mm-dd TO year-mm-dd range, or 'BACK' to return to analysis tools"
	
	date_entry = raw_input('Enter Date or Command: ')

	if date_entry == 'BACK':
		display_menu()

	elif 'TO' in date_entry:
		date_entry = date_entry.split(' TO ', 1)
		start = date_entry[0]
		end = date_entry[1]

		calories_and_exercise = list(c.execute('SELECT daily_totals.date, daily_totals.calories, exercise.exercise FROM 		daily_totals, exercise WHERE daily_totals.date BETWEEN ? AND ? AND daily_totals.date = exercise.date', (start, end,)))

		#Even if there's no food info available, there will almost certainly be a total calorie estimate and exercise record
		#When putting information into database, be sure that each date is represented, even if there's no info for it -- 
		#Empty values for food_entries, rather than be allowed to sit null, can be represented with 'unspecified' if need be
		if not calories_and_exercise:
			print "Error returning records for date range: "+start+" to "+end
			view_dates()

		else:
			for entry in calories_and_exercise:
				print "------------------------------------------------"+"\n"+entry[0]+"\n"
				print "Total calories: "+str(entry[1])
				print "Exercise: "+entry[2]+"\n"
				records = list(c.execute('SELECT * FROM food_entries WHERE date = ?', (entry[0],)))

				for record in records:
					print record[1]+"  "+record[2]+"  "+str(record[3])+record[4]
			print "------------------------------------------------"
		view_dates()


	else:
		calories_and_exercise = list(c.execute('SELECT daily_totals.calories, exercise.exercise FROM daily_totals, exercise WHERE 			daily_totals.date = ? AND daily_totals.date = exercise.date', (date_entry,)))

		if not calories_and_exercise:
			print "No records found for "+date_entry
			view_dates()

		else:
			records = list(c.execute('SELECT food_entries.time, food_entries.food, food_entries.calories, food_entries.estimated 				FROM food_entries WHERE food_entries.date = ?', (date_entry,)))

			print "------------------------------------------------"+"\n"+ date_entry+"\n"
			#Get first record to read calorie and exercise information from; 
			 
			for record in records:	
				print record[0]+"  "+record[1]+"  "+str(record[2])+"  "+record[3]

			print "\n"

			for item in calories_and_exercise:
				total_calories = item[0]				
				exercise = item[1]

			print "Total calories: "+str(total_calories)
			print "Exercise: "+exercise

			print "------------------------------------------------"

			view_dates()


def valid_date(datestring):
    try:
        datetime.datetime.strptime(datestring, '%Y-%m-%d')
        return True
    except ValueError:
        return False

def add_new_date():

	while True:
		#Will this cause scoping issues? 
		#-->No, control blocks don't count as defining a scope ring
		date = raw_input('Enter the date: ')
		
		if valid_date(date) == False:
			date = raw_input('Please re-enter the date as year-mm-dd: ')

		total_calories = raw_input('Enter total calories: ')
		exercise = raw_input('Enter exercise description: ')
	
		basic_data_row = date + " " + total_calories + " " + exercise
	
		print basic_data_row
	
		verify = raw_input('Enter Y if correct, N to re-enter the information: ')
	
		if verify.strip() == 'Y':
			#Insert into daily_totals table
			c.execute('INSERT INTO daily_totals VALUES (?, ?)', (date, total_calories))
			#Insert into exercise table
			exercise_entry = [(date, exercise)]
			c.execute('INSERT INTO exercise VALUES (?, ?)', (date, exercise))
			break

	print "Input food entries at the prompt."

	while True:
		while True:
			food = raw_input('Food name: ')
			time = raw_input('Time of consumption: ')
			calories = raw_input('Calories: ')
			estimated = raw_input('Enter V if calories verified, E if estimated: ' )
	   
			food_entries_row = food + " " + time + " " + calories + " " + estimated

			print food_entries_row
			correct = raw_input('Enter Y to save and continue, N to re-enter the row: ' )

			if correct.strip() == 'Y':
				#Insert into food_entries table
				c.execute('INSERT INTO food_entries VALUES (?,?,?,?,?)', (date, time, food, calories, estimated))
				break

		#After food item entered, check to make sure there is a corresponding info entry
		#If not, user will need to fill one in

		c.execute('SELECT * FROM food_info WHERE name = ?', (food,))

		corresponding_info = c.fetchall()

		if len(corresponding_info) == 0:
			print "This food item does not have an associated entry in the information table. Add one now: "

			while True:
				info_food = raw_input('Food name: ')
				food_type = raw_input('Food type: ')
				serving_size = raw_input('Serving size: ')
				calories_per_serving = raw_input('Calories per serving: ')

				food_info_row = info_food+" "+food_type+" "+serving_size+" "+calories_per_serving

				print food_info_row

				check = raw_input('Enter Y to save and continue, N to re-enter the row: ')

				if check.strip() == 'Y':
					#Insert into food_info table
					c.execute('INSERT INTO food_info VALUES (?,?,?,?)', (food, food_type, calories_per_serving, 							  serving_size))
					break	

		done = raw_input('Enter DONE if finished adding foods. If not, C to continue.: ')

		if done.strip() == 'DONE':
			#Commit changes to database and close
			connection.commit()
			
			display_menu() 

######## Run script:

display_menu()

