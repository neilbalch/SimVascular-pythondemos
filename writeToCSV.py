import csv

# Fill with data here.
data = []

file = csv.writer(open('data.csv', 'w'), delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)

for element in data:
  file.writerow(element)
