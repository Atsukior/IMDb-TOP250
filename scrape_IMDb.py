import csv
import re
import requests
from bs4 import BeautifulSoup

import pandas as pd
import matplotlib.pyplot as plt

with open('IMDb_TOP250.csv', 'w', newline='', encoding='utf-8-sig') as file: 
    csv_writer=csv.writer(file)
    headers = {
        "User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac 0S X 10_15_7) AppleWebKit/537.36 (KHTM,like Gecko) Chrome/109.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9"
    }
    response = requests.get("https://www.imdb.com/chart/top/",headers=headers)
    html = response.text
    soup = BeautifulSoup(html, "lxml")
    all_title = soup.find_all("h3")
    all_item = soup.find_all("span", attrs={"class": "sc-c7e5f54-8 hgjcbi cli-title-metadata-item"})
    all_rating = soup.find_all("span", attrs={"class":"ipc-rating-star ipc-rating-star--base ipc-rating-star--imdb ratingGroup--imdb-rating"})

    title_movies = []
    year_movies = []
    duration_movies = []
    classification_movies = []
    rate_movies = []
    number_graders = []

    for title in all_title:
        title_string = title.get_text()
        if "." in title_string:
            title_parts = title_string.split(". ")
            title_movies.append(title_parts[1])

    for year in all_item:
        if len(year.string) == 4:
            year_string = year.get_text()
            if  year_string.isdigit():
                year_movies.append(year.string)

    pattern = r"\d+h\s?\d+m|\d+h|\d+m"
    for duration in all_item:
        duration_string = duration.get_text()
        duration_match = re.search(pattern, duration_string)
        if duration_match:
            duration_movies.append(duration_match.group())

    for i in range(2, 228, 3):
        classification_movies.append(all_item[i].string)

    classification_movies.insert(76, "NULL")

    for j in range(232, 750, 3):
        classification_movies.append(all_item[j].string)

    for rate in all_rating:
        rate_movies.append(rate.text[:3])

    pattern = r'\((.*?)\)'  # 定义一个正则表达式模式，用于匹配括号内的内容
    for number in all_rating:
        number_string = number.get_text()
        match = re.search(pattern, number_string)
        if match:
            number_match = match.group(1)
            number_graders.append(number_match)

    movies = []

    for movie in zip(title_movies, year_movies, duration_movies, classification_movies, rate_movies, number_graders):
        movies.append(list(movie))
    
    csv_writer.writerow(['Ranking', 'Title', 'Year', 'Duration', 'Classification', 'Rating', 'Numbers'])
    for i, movie in enumerate(movies, start=1):
        csv_writer.writerow([i] + list(movie))
    print("成功爬取o.O?")

# 读取CSV文件
df = pd.read_csv('IMDb_TOP250.csv')

# 统计year_movies的分布情况
year_counts = df['Year'].value_counts()

# 绘制并保存year_movies的柱状图
plt.bar(year_counts.index, year_counts.values)
plt.xlabel('Year')
plt.ylabel('Count')
plt.title('Distribution of Movies by Year')
plt.savefig('year_movies.png')
plt.show()

# 创建时间段的列表
time_periods = ['<1h', '1h-1.5h', '1.5h-2h', '2h-2.5h', '2.5h-3h', '>3h']

# 清洗和预处理时长数据
df['Duration'] = df['Duration'].str.replace('h', 'h ')
df['Duration'] = df['Duration'].str.replace('m', 'm ')

# 提取小时和分钟信息，并将其转换为分钟数
def extract_duration(x):
    durations = re.findall(r'(\d+)(h|m)', x)
    total_minutes = 0
    for duration in durations:
        value, unit = duration
        if unit == 'h':
            total_minutes += int(value) * 60
        elif unit == 'm':
            total_minutes += int(value)
    return total_minutes

df['Duration'] = df['Duration'].apply(extract_duration)

# 将时长数据转换为时间段
df['Time Period'] = pd.cut(df['Duration'], [0, 60, 90, 120, 150, 180, 9999], labels=time_periods)

# 统计时间段的分布情况
duration_counts = df['Time Period'].value_counts()

# 绘制并保存duration_movies的饼状图
plt.pie(duration_counts.values, labels=duration_counts.index, autopct='%1.1f%%')
plt.title('Distribution of Movies by Time Period')
plt.savefig('duration_movies.png')
plt.show()

# 统计classification_movies的分布情况
classification_counts = df['Classification'].value_counts()

# 绘制并保存classification_movies的条形图
plt.barh(classification_counts.index[::-1], classification_counts.values[::-1])
plt.xlabel('Count')
plt.ylabel('Classification')
plt.title('Distribution of Movies by Classification')
plt.savefig('classification_movies.png')
plt.show()

# 统计rate_movies的分布情况
rate_counts = df['Rating'].value_counts().sort_index()

# 绘制并保存rate_movies的折线图
plt.plot(rate_counts.index, rate_counts.values, marker='o', linestyle='-', linewidth=2)
plt.xlabel('Rating')
plt.ylabel('Count')
plt.title('Distribution of Movies by Rating')
plt.savefig('rate_movies.png')
plt.show()

# 定义一个函数，用于将评价人数的字符串转换为整数
def convert_to_int(value):
    if value.endswith('M'):  # 如果字符串以'M'结尾，表示以百万为单位
        return int(float(value[:-1]) * 1000000)  # 将字符串转换为浮点数，去除最后一个字符'M'，并乘以1000000转换为整数
    elif value.endswith('K'):  # 如果字符串以'K'结尾，表示以千为单位
        return int(float(value[:-1]) * 1000)  # 将字符串转换为浮点数，去除最后一个字符'K'，并乘以1000转换为整数
    else:
        return int(value)  # 否则，直接将字符串转换为整数
    
# 将'Numbers'列的数据应用转换函数，将评价人数的字符串转换为整数
df['Numbers'] = df['Numbers'].apply(convert_to_int)

# 获取评分列和转换后的评价人数列
rate_movies = df['Rating']
number_graders = df['Numbers']

# 绘制并保存rate_movies与number_graders的散点图
plt.scatter(rate_movies, number_graders)
plt.xlabel('Rating')
plt.ylabel('Number of Graders')
plt.title('Relationship between Rating and Number of Graders')
plt.savefig('rating_vs_graders.png')
plt.show()