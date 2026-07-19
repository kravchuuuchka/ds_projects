from movies import Movies
from ratings import Ratings, average, median, variance
from tags import Tags
from links import Links


__all__ = [
    "Movies", "Ratings", "Tags", "Links", "average", "median", "variance"
]

if __name__=='__main__':
    a=Movies(limit=20)
    print(a.get_movies())