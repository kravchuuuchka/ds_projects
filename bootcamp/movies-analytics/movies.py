from collections import Counter
import os
import re


class Movies:

    def __init__(self, path='./ml-latest-small/movies.csv', limit=1000):
        self.path = path
        self.limit = limit
        self.movies = []
        self.load_data()

    def load_data(self):
       

        if not os.path.exists(self.path):
            raise FileNotFoundError("Movies file not found")
            
        with open(self.path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        for line in lines[1:self.limit]: 
            line_str = line.strip()
            if not line_str:
                continue

            parts = re.split(r',(?=(?:[^"]*"[^"]*")*[^"]*$)', line_str)
            
            if len(parts) < 3:
                continue
            # распихиваем по переменным
            movieID = parts[0].strip()
            title_raw = parts[1].strip()
            genres = parts[2].strip()

            
            if title_raw.startswith('"') and title_raw.endswith('"'):
                title_raw = title_raw[1:-1].strip()

            match = re.search(r'\s*\((\d{4})\)$', title_raw)
            
            if match:
                year = match.group(1) 
                title = title_raw[:match.start()].strip() 
            else:
                year = ""
                title = title_raw

            genre_list = [genre.strip() for genre in genres.split('|') if genre.strip() != "(no genres)"]
            if not genre_list:
                genre_list = ['(no genres)']
    
            self.movies.append({
                        'movieID': movieID,
                        'title': title,
                        'release': year,
                        'genres': genre_list
                    })

    
    def dist_by_release(self):
        release_years = Counter(movie['release'] for movie in self.movies if movie['release'] is not None and movie['release'] != "")
        return dict(release_years.most_common())
    
    def dist_by_genres(self):
        genres = Counter(genre for movie in self.movies for genre in movie['genres'])
        return dict(genres.most_common())
        
    def most_genres(self, n):
        genre_counts = Counter(genre for movie in self.movies for genre in movie['genres'])
        most_common_genres = genre_counts.most_common(n)
        return dict(most_common_genres)

    def get_movies(self):
        return self.movies.copy()
    

if __name__ == "__main__":
    # Movies()
    a=Movies().get_movies()

    # print(a)
    print(Movies().dist_by_genres())
    print(Movies().dist_by_release())
    print(Movies().most_genres(2))
