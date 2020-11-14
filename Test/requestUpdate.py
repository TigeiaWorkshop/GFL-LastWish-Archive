import urllib.request as request
import csv
r = request.urlopen('https://raw.githubusercontent.com/yudonglin/Oregon-Trail/master/README.txt').read().decode('utf8').split("\n")
reader = csv.reader(r)
for line in reader:
    print(line)