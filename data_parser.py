
# Import necessary packages and functions
import glob
import os
import csv
import xml.etree.ElementTree as ET

def data_parser():

    # Print the header of the parser to the screen
    print('\nEndomondo Data Parser')

    # Collect all file names in a specified directory
    path = './data/raw/'
    filenames = []
    for files in glob.glob(os.path.join(path, '*.tcx')):
        filenames.append(files)

    # Print number of files found in the directory
    print('\nTotal', len(filenames), 'files found in path:', path, '\n\n=====================')

    # Extract summary data records and write to .csv file
    extract_summary_data(filenames)

    # Extract tracking data records and write to .csv file
    extract_tracking_data(filenames)

def extract_summary_data(filenames):
	'''
	Extract the summary data from filenames and write it to .csv file
	'''

	fs_path = './data/parsed/'
	fs = 'summary_data.csv'
	ws = open(fs_path + fs, 'w', newline = '')
	write_summary = csv.writer(ws)
	head_summary = ['activity_id', 'file_name', 'sport_type', 'start_date',
                    'start_time', 'total_time', 'total_distance', 'total_calories']
	write_summary.writerow(head_summary)

	print('\nFile', fs, 'was created with', len(head_summary), 'columns:')
	for hs in head_summary:
		print(hs)

	activity_id = 0
	for fname in filenames:
		tree = ET.parse(fname)
		root = tree.getroot()
		namespace = {'ns': 'http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2'}
		summary_data = root.findall('ns:Activities/ns:Activity', namespace)
		for s in summary_data:
			sport_type = s.get('Sport')
			start_datetime = s.find('ns:Lap', namespace).get('StartTime')
			total_time = s.find('ns:Lap', namespace).find('ns:TotalTimeSeconds', namespace).text
			total_time_ = round(float(total_time))
			total_distance = s.find('ns:Lap', namespace).find('ns:DistanceMeters', namespace).text
			total_distance_ = round(float(total_distance), 2)
			total_calories = s.find('ns:Lap', namespace).find('ns:Calories', namespace).text
		activity_id += 1
		lines_summary = [activity_id, fname[-19:], sport_type, start_datetime[:10],
                   start_datetime[11:19], total_time_, total_distance_, total_calories]
		write_summary.writerow(lines_summary)

	print('\nFile', fs, 'was appended with', activity_id, 'records.', '\n\n=====================')

def extract_tracking_data(filenames):
	'''
	Extract the tracking data from filenames and write it to .csv file
	'''

	ft_path = './data/parsed/'
	ft = 'tracking_data.csv'
	wt = open(ft_path + ft, 'w', newline = '')
	write_tracking = csv.writer(wt)
	head_tracking = ['activity_id', 'tracking_id', 'tracking_time',
                     'tracking_latitude', 'tracking_longitude', 'tracking_distance']
	write_tracking.writerow(head_tracking)

	print('\nFile', ft, 'was created with', len(head_tracking), 'columns:')
	for ht in head_tracking:
		print(ht)

	counter = 0
	activity_id = 0
	for fname in filenames:
		tree = ET.parse(fname)
		root = tree.getroot()
		namespace = {'ns': 'http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2'}
		tracking_data = root.findall('ns:Activities/ns:Activity/ns:Lap/ns:Track/ns:Trackpoint', namespace)
		tracking_id = 0
		activity_id += 1
		for t in tracking_data:
			tracking_time = t.find('ns:Time', namespace).text
			tracking_latitude = t.find('ns:Position', namespace).find('ns:LatitudeDegrees', namespace).text
			tracking_longitude = t.find('ns:Position', namespace).find('ns:LongitudeDegrees', namespace).text
			tracking_distance = t.find('ns:DistanceMeters', namespace).text
			tracking_distance_ = round(float(tracking_distance), 2)
			tracking_id += 1
			counter += 1
			lines_tracking = [activity_id, tracking_id, tracking_time[11:19],
                       tracking_latitude, tracking_longitude, tracking_distance_]
			write_tracking.writerow(lines_tracking)

	print('\nFile', ft, 'was appended with', counter, 'records.')

if __name__ == "__main__":
    data_parser()
