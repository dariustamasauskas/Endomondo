
# Import necessary packages and functions
import glob
import os
import Endomondo_parsing_functions as PF

# Print the header of the parser to the screen
print('\nEndomondo Data Parser')

# Collect all file names in a specified directory
path = 'E:\Career\Data Science\Projects\Workshop\Endomondo\Raw Data'
filenames = []
for files in glob.glob(os.path.join(path,'*.tcx')):
    filenames.append(files)

# Print number of files found in the directory
print('\nTotal',len(filenames),'files found in path:',path,'\n\n=====================')

# Extract summary data records and write to .csv file
PF.extract_summary_data(filenames)

# Extract tracking data records and write to .csv file
PF.extract_tracking_data(filenames)
