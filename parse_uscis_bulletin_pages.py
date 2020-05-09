#!/usr/bin/python3

import urllib.request
import lxml.html
import pandas
import dateutil
from matplotlib import pyplot as plt
import matplotlib.dates as mdates
import os


BASEURL = 'https://travel.state.gov'
VISABULLETTINS = BASEURL + '/content/travel/en/legal/visa-law0/visa-bulletin.html'
FY = 2016

vb_index = urllib.request.urlopen(VISABULLETTINS).read()
tree = lxml.html.fromstring(vb_index)

bulletins = set()
for link in tree.iterlinks():
    # example of a link: "/content/travel/en/legal/visa-law0/visa-bulletin/2020/visa-bulletin-for-may-2020.html"
    if '/visa-bulletin/' in link[2]:
        # select only Visa Bulletin from a few latest fiscal years
        # Note: US Govt FYs starts on October, and they are part of the URL components
        if int(link[2].split('/')[7]) >= FY:
            bulletins.add(BASEURL + link[2])

file_dates = dict()

for bulletin in bulletins:
    # the month the bulletin refers to
    current_month = dateutil.parser.parse('1 ' + bulletin.split('/')[-1].replace('visa-bulletin-for-', '').replace('.html', ''))

    data = pandas.read_html(bulletin)
    for table in data:
        # there are multiple tables, we care about only the first one about "Employment-based" sponsorship
        if 'employment' in table[0][0].lower():
            # get only the EB3 for "All Chargeability Areas Except Those Listed"
            file_date = table[1][3]
            if file_date == 'C':
                file_dates[current_month] = current_month
            else:
                file_dates[current_month] = dateutil.parser.parse(file_date)
            break

# generate the EB3 graphs
plt_locator = mdates.MonthLocator(interval=2)
plt_formatter = mdates.AutoDateFormatter(plt_locator)
fig, ax = plt.subplots()
fig.set_size_inches(16, 10)
ax.xaxis.set_major_locator(plt_locator)
ax.xaxis.set_major_formatter(plt_formatter)
plt.title(f"Waiting time (in months) for filing EB3; FY {FY} to current")
ax.set_ylabel('Months')
ax.set_xlabel('Visa Bulletin Date')

ax.plot(sorted(file_dates.keys()), [(date - file_dates[date]).days // 30 for date in sorted(file_dates.keys())], label='EB3 waiting time')

plt.xticks(rotation=18, ha='right')
plt.grid()
fig.tight_layout()
ax.legend(loc='upper left')
os.makedirs('images', exist_ok=True)
plt.savefig('images/EB3.svg')
