import csv
import re
import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt

def get_html_content(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac 0S X 10_15_7) AppleWebKit/537.36 (KHTM,like Gecko) Chrome/109.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9"
    }
    response = requests.get(url, headers=headers)
    return response.text

def get_movie_details(html):
    soup = BeautifulSoup(html, "lxml")
    all_title = soup.find_all("h3")
    all_item = soup.find_all("span", attrs={"class": "sc-c7e5f54-8 hgjcbi cli-title-metadata-item"})
    all_rating = soup.find_all("span", attrs={"class":"ipc-rating-star ipc-rating-star--base ipc-rating-star--imdb ratingGroup--imdb-rating"})

    title_movies = [title.get_text().split('. ')[1] for title in all_title if "." in title.get_text()]
    
    year_movies = [item.string for item in all_item if len(item.string) == 4 and item.string.isdigit()]

    pattern = r"\d+h\s?\d+m|\d+h|\d+m"
    duration_movies = [re.search(pattern, duration.get_text()).group() for duration in all_item if re.search(pattern, duration.get_text())]

    classification_movies = [all_item[i].string for i in range(2, 228, 3)]
    classification_movies.insert(76, "NULL")
    classification_movies += [all_item[j].string for j in range(232, 750, 3)]

    rate_movies = [rate.text[:3] for rate in all_rating]

    pattern = r'\((.*?)\)'
    number_graders = [re.search(pattern, number.get_text()).group(1) for number in all_rating if re.search(pattern, number.get_text())]
    
    movies = list(zip(title_movies, year_movies, duration_movies, classification_movies, rate_movies, number_graders))
    return movies

def save_to_csv(movies):
    with open('IMDb_TOP250_plus.csv', 'w', newline='', encoding='utf-8-sig') as file:
        csv_writer = csv.writer(file)
        csv_writer.writerow(['Ranking', 'Title', 'Year', 'Duration', 'Classification', 'Rating', 'Numbers'])
        for i, movie in enumerate(movies, start=1):
            csv_writer.writerow([i] + list(movie))
        print("成功爬取！")

def read_from_csv():
    df = pd.read_csv('IMDb_TOP250_plus.csv')
    return df

def plot_year_distribution(df):
    year_counts = df['Year'].value_counts()
    plt.bar(year_counts.index, year_counts.values)
    plt.xlabel('Year')
    plt.ylabel('Count')
    plt.title('Distribution of Movies by Year')
    plt.show()

def plot_duration_distribution(df):
    time_periods = ['<1h', '1h-1.5h', '1.5h-2h', '2h-2.5h', '2.5h-3h', '>3h']

    df['Duration'] = df['Duration'].str.replace('h', 'h ').str.replace('m', 'm ').apply(lambda x: sum([int(num[:-1]) * (60 if 'h' in num else 1) for num in re.findall(r'\d+[hm]', x)]) if re.findall(r'\d+[hm]', x) else None)

    df['Time Period'] = pd.cut(df['Duration'], [0, 60, 90, 120, 150, 180, 9999], labels=time_periods)

    duration_counts = df['Time Period'].value_counts()
    plt.pie(duration_counts.values, labels=duration_counts.index, autopct='%1.1f%%')
    plt.title('Distribution of Movies by Time Period')
    plt.show()

def plot_classification_distribution(df):
    classification_counts = df['Classification'].value_counts()
    plt.barh(classification_counts.index[::-1], classification_counts.values[::-1])
    plt.xlabel('Count')
    plt.ylabel('Classification')
    plt.title('Distribution of Movies by Classification')
    plt.show()

def plot_rating_distribution(df):
    rate_counts = df['Rating'].value_counts().sort_index()
    plt.plot(rate_counts.index, rate_counts.values, marker='o', linestyle='-', linewidth=2)
    plt.xlabel('Rating')
    plt.ylabel('Count')
    plt.title('Distribution of Movies by Rating')
    plt.show()

def convert_to_int(value):
    if value.endswith('M'):
        return int(float(value[:-1]) * 1000000)
    elif value.endswith('K'):
        return int(float(value[:-1]) * 1000)
    else:
        return int(value)

def plot_rating_vs_graders(df):
    df['Numbers'] = df['Numbers'].apply(convert_to_int)
    rate_movies = df['Rating']
    number_graders = df['Numbers']
    plt.scatter(rate_movies, number_graders)
    plt.xlabel('Rating')
    plt.ylabel('Number of Graders')
    plt.title('Relationship between Rating and Number of Graders')
    plt.show()

html_content = get_html_content("https://www.imdb.com/chart/top/")
movies = get_movie_details(html_content)
save_to_csv(movies)

df = read_from_csv()

plot_year_distribution(df)

plot_duration_distribution(df)

plot_classification_distribution(df)

plot_rating_distribution(df)

plot_rating_vs_graders(df)
