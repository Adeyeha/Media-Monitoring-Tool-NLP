## NLP-Based Web Application for Sentiment Analysis on Google Feeds
This is an NLP-based web application that performs sentiment analysis on Google feeds. The application is designed for organizations that want to monitor media news about their competitors, customers, or any other relevant topic. The application uses natural language processing techniques to analyze the sentiment of news articles and other online content, providing real-time feedback to users.

### Requirements
- Python 3.x
- Django
- NLTK
- TextBlob
- Google News API

### How to run
Clone the repository and navigate to the directory.

``` sh
git clone https://github.com/<repo-url>.git
cd <repo-directory>
```
Install the required libraries:

``` sh
pip install -r requirements.txt
```
Run the Django development server:

``` sh
python manage.py runserver
```
The application will be available at http://localhost:8000/.

### Features
- Real-time sentiment analysis of Google feeds
- User-friendly dashboard to view analysis results
- Interactive charts to visualize the sentiment trends
- Option to monitor different topics or keywords

### How it works
The application uses the Google News API to collect news articles and other online content related to the specified topics or keywords. It then uses NLTK and TextBlob libraries to perform sentiment analysis on the collected data. The analysis results are then displayed on the web application dashboard, which includes interactive charts to visualize the sentiment trends.

### Contributing
If you want to contribute to this project, please create a pull request with a detailed description of your changes.

### License
MIT

### Authors
[Temitope Adeyeha](https://github.com/Adeyeha)
Ridwan Salahudeen

