# This module handles analytical DB queries and works with Visualization_Tools to generate graphic output 
#For the time being: This has no interface with Database_Tools, which exists just to fill the tables and do a few simple viewing queries.

import sqlite3
import sys
import datetime
import Visualization_Tools as visual_tools
from dateutil import parser

connection = sqlite3.connect('/path/to/your/diet_data.db')

connection.text_factory = str
connection.row_factory = sqlite3.Row

c = connection.cursor()

def display_menu():
	print "Enter CALORIE-DRIVEN to perform analyses concerned primarily with calories consumed."
	#print "Enter EXERCISE-DRIVEN for analyses concerned primarily with exercise."
	#print "Enter FOOD-RECORD-DRIVEN for analyses conerning foods, times of consumption, calorie breakdowns, etc."
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

	else:
		print 'Command '+nav_command+' not found.'
		display_menu()

def calorie_analysis():
	print "Enter the number of the analysis to query on and produce listed, visualization-ready data: "
	print "1. View total calories over a range of dates. For viewing entries as text in terminal, use Database_Tools.view_dates()"
	print "2. Sum up total calorie count for a range of dates."
	#print "3. Calculate a BMR (whose fluctuation can be approximately computed) and compare it a date range of calories consumed."
	
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

	else:
		print 'Command '+nav_command+' not found.'
		calorie_analysis()

#####Run script

display_menu()
