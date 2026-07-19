import os
from collections import Counter
from datetime import datetime

class Tags:
   
    def __init__(self, path='./ml-latest-small/tags.csv', limit=1000):

        if not os.path.isfile(path) or os.path.getsize(path) == 0:
            raise FileNotFoundError(f"Файл не найден или пустой: {path}")
        self.path=path
        self.limit=limit
        self.tags = []
        with open(self.path, 'r', encoding='utf-8') as f:
            lines = f.readlines()  
            try:
                 for line in lines[1:self.limit]:
                    parts = line.strip().split(',', 3) 
                    if not parts or len(parts) < 4:
                        continue 
                    
                    user_id = int(parts[0])
                    movie_id = int(parts[1])
                    tag = parts[2]
                    timestamp = int(parts[3])
                    self.tags.append({'userId': user_id, 'movieId': movie_id, 'tag': tag, 'timestamp': timestamp})
                    
            except Exception as e: 
                print(f"Error during tag loading: {e}")

    def most_words(self, n=5):

        if not isinstance(n, int) or n <= 0:
            raise ValueError(f"Invalid argument value: {n}")
        
        unique_tags = set(i['tag'].strip().lower() for i in self.tags)
        counts = {tag: len(tag.split()) for tag in unique_tags}
        big_tags = dict(sorted(counts.items(), key=lambda x: x[1], reverse=True)[:n])
        
        return big_tags

    def longest(self, n=5):
        
        if not isinstance(n, int) or n <= 0:
            raise ValueError(f"Invalid argument value: {n}")
        
        unique_tags = set(i['tag'].strip().lower() for i in self.tags)
        counts = {tag: len(tag) for tag in unique_tags}
        big_tags = dict(sorted(counts.items(), key=lambda x: x[1], reverse=True)[:n])
        return big_tags


    def most_words_and_longest(self, n=5):

        if not isinstance(n, int) or n <= 0:
            raise ValueError(f"Invalid argument value: {n}")
    
        most_words_tags = set(self.most_words(n).keys())
        longest_tags = set(self.longest(n).keys())
        intersection = most_words_tags & longest_tags
        big_tags  =  sorted(intersection)

        return big_tags
        
    def most_popular(self, n=5):

        if not isinstance(n, int) or n <= 0:
            raise ValueError(f"Invalid argument value: {n}")
        
        tag_list = [i['tag'].strip().lower() for i in self.tags]
        counter = Counter(tag_list)
    
        popular_tags = dict(counter.most_common(n))
    
        return popular_tags
        
    def tags_with(self, word):

        if not isinstance(word, str) or not word.strip():
            raise ValueError(f"Invalid word for search: {word}")

        word = word.strip().lower()
        
        matching_tags = {
            i['tag'].strip().lower()
            for i in self.tags
            if word in i['tag'].strip().lower()
        }

        tags_with_word =  sorted(matching_tags)

        return tags_with_word

    def dist_by_year(self):
        years = []
        for tag in self.tags:
            ts = tag.get('timestamp')
            if ts:
                year = datetime.fromtimestamp(ts).year
                years.append(year)
        annual_tags = dict(Counter(years).most_common())
        return annual_tags
    
    def get_tags(self):
        return self.tags.copy()
    

if __name__ == '__main__':

    a = Tags()
    t=a.get_tags()
    # print(t)
    print(a.most_words(3))
    print(a.longest(3))
    print(a.most_words_and_longest(3))
    print(a.tags_with('fun'))

    print(a.dist_by_year())