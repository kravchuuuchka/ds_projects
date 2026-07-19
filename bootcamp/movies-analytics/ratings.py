import os
from datetime import datetime, timezone
from collections import defaultdict
from typing import Callable


def average(values: list[float]) -> float:
    '''
    Вычисляет среднее арифметическое списка чисел.
    Аргументы: values: список числовых значений.
    Возвращает: среднее арифметическое или 0.0, если список пуст.
    '''
    return sum(values) / len(values) if values else 0.0


def median(values: list[float]) -> float:
    '''
    Вычисляет медиану списка чисел.
    Аргументы: values: список числовых значений.
    Возвращает: медиану или 0.0 если список пуст.
    '''
    if not values:
        return 0.0
    s = sorted(values)
    n = len(s)
    mid = n // 2
    return (s[mid] if n % 2 != 0 else (s[mid - 1] + s[mid]) / 2)


def variance(values: list[float]) -> float:
    '''
    Вычисляет дисперсию списка чисел.
    Аргументы: values: список числовых значений.
    Возвращает: дисперсию или 0.0 если список содержит менее двух элементов.
    '''
    if len(values) < 2:
        return 0.0
    avg = average(values)
    return sum((x - avg) ** 2 for x in values) / len(values)


class Ratings:
    def __init__(self, path_to_ratings: str, path_to_movies: str) -> None:
        self.ratings_path = path_to_ratings
        self.movies_path = path_to_movies
        self.data = self._load_data(limit=1000)
        self.movies = Ratings.Movies(self.data)
        self.users = Ratings.Users(self.data)

    def _load_data(self, limit: int = 1000) -> list[dict]:
        '''
        Читает первые 1000 строк из ratings.csv и movies.csv,
        объединяет их по movieId в один список словарей.
        Аргументы: limit: максимальное количество фильмов для загрузки
        Возвращает: список словарей с полями
                    userId, movieId, title, genres, rating, timestamp
        '''
        if not os.path.exists(self.ratings_path):
            raise FileNotFoundError(f"File not found: {self.ratings_path}")
        if not os.path.exists(self.movies_path):
            raise FileNotFoundError(f"File not found: {self.movies_path}")

        def parse_line(line: str) -> list[str]:
            result = []
            current = []
            in_quotes = False

            for char in line.strip():
                if char == '"':
                    in_quotes = not in_quotes
                elif char == ',' and not in_quotes:
                    result.append(''.join(current))
                    current = []
                else:
                    current.append(char)

            result.append(''.join(current))
            return result

        with open(self.movies_path, encoding='utf-8') as f:
            lines = f.readlines()

        movies_header = parse_line(lines[0])

        movies = {
            row['movieId']: {
                'title': row['title'],
                'genres': row['genres'],
            }
            for row in (
                dict(zip(movies_header, parse_line(line)))
                for line in lines[1:limit + 1]
            )
        }

        with open(self.ratings_path, encoding='utf-8') as f:
            lines = f.readlines()

        ratings_header = parse_line(lines[0])

        ratings = [
            dict(zip(ratings_header, parse_line(line)))
            for line in lines[1:]
        ]

        merged = []

        for row in ratings:
            movie_id = row['movieId']

            if movie_id not in movies:
                continue

            merged.append({
                'userId': row['userId'],
                'movieId': movie_id,
                'title': movies[movie_id]['title'],
                'genres': movies[movie_id]['genres'],
                'rating': float(row['rating']),
                'timestamp': int(row['timestamp']),
            })

        return merged

    class Movies:
        def __init__(self, data: list[dict]) -> None:
            self._data = data
            self._valid_keys = {'title', 'userId', 'movieId', 'genres'}
            self._valid_metrics = {'average', 'median'}

        def _get_groups(self, key: str = 'title') -> dict[str, list[float]]:
            '''
            Группирует рейтинги по заданному полю строки данных.
            Аргументы: key: название поля для группировки ('title' или 'userId').
            Возвращает: словарь {значение_ключа: [рейтинги]}.
            '''
            if key not in self._valid_keys:
                raise KeyError(f"invalid grouping key '{key}', valid keys: {self._valid_keys}")
            result: dict[str, list[float]] = defaultdict(list)
            for row in self._data:
                result[row[key]].append(row['rating'])
            return result

        def dist_by_year(self) -> dict[int, int]:
            '''
            Считает количество оценок по годам.
            Возвращает: словарь {год: количество_оценок}, отсортированный по году по возрастанию.
            '''
            counts: dict[int, int] = defaultdict(int)
            for row in self._data:
                year = datetime.fromtimestamp(row['timestamp'], tz=timezone.utc).year
                counts[year] += 1
            return dict(sorted(counts.items()))

        def dist_by_rating(self) -> dict[float, int]:
            '''
            Считает количество оценок для каждого значения рейтинга.
            Возвращает: словарь {рейтинг: количество}, отсортированный по рейтингу по возрастанию.
            '''
            counts: dict[float, int] = defaultdict(int)
            for row in self._data:
                counts[row['rating']] += 1
            return dict(sorted(counts.items()))

        def top_by_num_of_ratings(self, n: int, key: str = 'title') -> dict[str, int]:
            '''
            Возвращает топ-n фильмов по количеству полученных оценок.
            Аргументы: n: количество записей в результате;
                       key: поле группировки (по умолчанию 'title').
            Возвращает: словарь {название_фильма: количество_оценок},
                        отсортированный по убыванию количества.
            '''
            if n <= 0:
                raise ValueError(f"n must be non-negative, got {n}")
            if key not in self._valid_keys:
                raise KeyError(f"invalid grouping key '{key}', valid keys: {self._valid_keys}")
            groups = self._get_groups(key)
            counts = {k: len(ratings) for k, ratings in groups.items()}
            top = sorted(counts.items(), key=lambda x: x[1], reverse=True)[:n]
            return dict(top)

        def top_by_ratings(self, n: int, metric: Callable = average, key: str = 'title') -> dict[str, float]:
            '''
            Возвращает топ-n фильмов по среднему или медианному рейтингу.
            Аргументы: n: количество записей в результате;
                       metric: функция агрегации (average или median);
                       key: поле группировки (по умолчанию 'title').
            Возвращает: словарь {название_фильма: значение_метрики},
                        отсортированный по убыванию, значения округлены до 2 знаков.
            '''
            if n <= 0:
                raise ValueError(f"n must be non-negative, got {n}")
            if key not in self._valid_keys:
                raise KeyError(f"invalid grouping key '{key}', valid keys: {self._valid_keys}")
            if not callable(metric) or getattr(metric, '__name__', None) not in self._valid_metrics:
                raise ValueError(f"invalid metric '{metric}', valid metrics: {self._valid_metrics}")
            groups = self._get_groups(key)
            scores = {k: round(metric(ratings), 2) for k, ratings in groups.items()}
            top = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:n]
            return dict(top)

        def top_controversial(self, n: int, key: str = 'title') -> dict[str, float]:
            '''
            Возвращает топ-n фильмов с наибольшей дисперсией оценок.
            Аргументы: n: количество записей в результате;
                       key: поле группировки (по умолчанию 'title').
            Возвращает: словарь {название_фильма: дисперсия},
                        отсортированный по убыванию, значения округлены до 2 знаков.
            '''
            if n <= 0:
                raise ValueError(f"n must be non-negative, got {n}")
            if key not in self._valid_keys:
                raise KeyError(f"invalid grouping key '{key}', valid keys: {self._valid_keys}")
            groups = self._get_groups(key)
            variances = {k: round(variance(ratings), 2) for k, ratings in groups.items()}
            top = sorted(variances.items(), key=lambda x: x[1], reverse=True)[:n]
            return dict(top)

        def users_who_rated(self, movie_title: str) -> list[str]:
            '''
            Возвращает список пользователей, оценивших указанный фильм.
            Аргументы: movie_title - название фильма.
            Возвращает: список userId пользователей, оценивших фильм.
            '''
            return [row['userId'] for row in self._data if row['title'] == movie_title]

        def rating_trend_by_year(self, movie_title: str) -> dict[int, float]:
            '''
            Показывает динамику среднего рейтинга фильма по годам.
            Аргументы: movie_title - название фильма.
            Возвращает: словарь {год: средний_рейтинг},
                        отсортированный по году по возрастанию, значения округлены до 2 знаков.
            '''
            by_year: dict[int, list[float]] = defaultdict(list)
            for row in self._data:
                if row['title'] == movie_title:
                    year = datetime.fromtimestamp(row['timestamp'], tz=timezone.utc).year
                    by_year[year].append(row['rating'])
            return dict(sorted(
                {year: round(average(ratings), 2) for year, ratings in by_year.items()}.items()
            ))


    class Users(Movies):
        def __init__(self, data: list[dict]) -> None:
            super().__init__(data)

        def top_by_num_of_ratings(self, n: int) -> dict[str, int]:
            '''
            Возвращает топ-n пользователей по количеству выставленных оценок.
            Аргументы: n: количество записей в результате.
            Возвращает: словарь {userId: количество_оценок},
                        отсортированный по убыванию количества.
            '''
            if n <= 0:
                raise ValueError(f"n must be non-negative, got {n}")
            return super().top_by_num_of_ratings(n, key='userId')

        def top_by_ratings(self, n: int, metric: Callable = average) -> dict[str, float]:
            '''
            Возвращает топ-n пользователей по среднему или медианному рейтингу.
            Аргументы: n: количество записей в результате;
                       metric: функция агрегации (average или median).
            Возвращает: словарь {userId: значение_метрики},
                        отсортированный по убыванию, значения округлены до 2 знаков.
            '''
            if n <= 0:
                raise ValueError(f"n must be non-negative, got {n}")
            if not callable(metric) or getattr(metric, '__name__', None) not in self._valid_metrics:
                raise ValueError(f"invalid metric '{metric}', valid metrics: {self._valid_metrics}")
            return super().top_by_ratings(n, metric=metric, key='userId')

        def top_controversial(self, n: int) -> dict[str, float]:
            '''
            Возвращает топ-n пользователей с наибольшей дисперсией выставленных оценок.
            Аргументы: n: количество записей в результате.
            Возвращает: словарь {userId: дисперсия},
                        отсортированный по убыванию.
            '''
            if n <= 0:
                raise ValueError(f"n must be non-negative, got {n}")
            return super().top_controversial(n, key='userId')

        def dist_by_num_of_ratings(self) -> dict[str, int]:
            '''
            Считает количество оценок, выставленных каждым пользователем.
            Возвращает: словарь {userId: количество_оценок},
                        отсортированный по возрастанию количества.
            '''
            counts = {k: len(v) for k, v in self._get_groups('userId').items()}
            return dict(sorted(counts.items(), key=lambda x: x[1]))

        def dist_by_ratings(self, metric: Callable = average) -> dict[str, float]:
            '''
            Считает средний или медианный рейтинг каждого пользователя.
            Аргументы: metric: функция агрегации (average или median).
            Возвращает: словарь {userId: значение_метрики},
                        отсортированный по возрастанию, значения округлены до 2 знаков.
            '''
            if not callable(metric) or getattr(metric, '__name__', None) not in self._valid_metrics:
                raise ValueError(f"invalid metric '{metric}', valid metrics: {self._valid_metrics}")
            scores = {k: round(metric(v), 2) for k, v in self._get_groups('userId').items()}
            return dict(sorted(scores.items(), key=lambda x: x[1]))

        def top_active_by_period(self, n: int, year: int) -> dict[str, int]:
            '''
            Возвращает топ-n наиболее активных пользователей за указанный год.
            Аргументы: n: количество записей в результате;
                       year: год в числовом формате.
            Возвращает: словарь {userId: количество_оценок},
                        отсортированный по убыванию количества.
            '''
            if n <= 0:
                raise ValueError(f"n must be non-negative, got {n}")
            if not str(year).isdigit():
                raise ValueError(f"year must be a positive integer, got {year!r}")
            counts: dict[str, int] = defaultdict(int)
            for row in self._data:
                if datetime.fromtimestamp(row['timestamp'], tz=timezone.utc).year == year:
                    counts[row['userId']] += 1
            top = sorted(counts.items(), key=lambda x: x[1], reverse=True)[:n]
            return dict(top)

        def movies_rated_by_user(self, user_id: int | str) -> list[str]:
            '''
            Возвращает список фильмов, оценённых указанным пользователем.
            Аргументы: user_id: числовой идентификатор пользователя.
            Возвращает: список названий фильмов.
            '''
            uid = str(user_id)
            if not uid.isdigit():
                raise ValueError(f"user_id must be numeric, got: {uid!r}")
            result = [row['title'] for row in self._data if row['userId'] == uid]
            if not result:
                raise LookupError(f"user '{uid}' not found")
            return result

        def top_movies_for_user(self, user_id: int | str, n: int) -> dict[str, float]:
            '''
            Возвращает топ-n фильмов с наивысшими оценками указанного пользователя.
            Аргументы: user_id: числовой идентификатор пользователя;
                       n: количество записей в результате.
            Возвращает: словарь {название_фильма: оценка},
                        отсортированный по убыванию оценки.
            '''
            uid = str(user_id)
            if not uid.isdigit():
                raise ValueError(f"user_id must be numeric, got: {uid!r}")
            if n <= 0:
                raise ValueError(f"n must be non-negative, got {n}")
            user_rows = [row for row in self._data if row['userId'] == uid]
            if not user_rows:
                raise LookupError(f"user '{uid}' not found")
            top = sorted(user_rows, key=lambda x: x['rating'], reverse=True)[:n]
            return {row['title']: row['rating'] for row in top}