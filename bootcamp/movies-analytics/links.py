import os
import json
import time
import random
import requests
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional


class Links:
    def __init__(self, path_to_links: str, path_to_movies: str) -> None:
        self.path_to_links = path_to_links
        self.path_to_movies = path_to_movies
        self.data = self._load_data()
        self._imdb_cache_path = path_to_links.replace(".csv", "_imdb_cache.json")
        self._tmdb_cache_path = path_to_links.replace(".csv", "_tmdb_cache.json")
        self._cache = self._load_cache(self._imdb_cache_path)
        self._tmdb_cache = self._load_cache(self._tmdb_cache_path)

    def _load_data(self, limit: int = 1000) -> list[dict]:
        """
        Читает первые limit строк из links.csv и movies.csv,
        объединяет их по movieId в один список словарей.
        Аргументы: limit: максимальное количество фильмов для загрузки
        Возвращает: список словарей с полями movieId, imdbId, tmdbId, title, genres
        """
        if not os.path.exists(self.path_to_links):
            raise FileNotFoundError(f"File not found: {self.path_to_links}")
        if not os.path.exists(self.path_to_movies):
            raise FileNotFoundError(f"File not found: {self.path_to_movies}")

        def parse_line(line: str) -> list[str]:
            result = []
            current = []
            in_quotes = False

            for char in line.strip():
                if char == '"':
                    in_quotes = not in_quotes
                elif char == "," and not in_quotes:
                    result.append("".join(current))
                    current = []
                else:
                    current.append(char)

            result.append("".join(current))
            return result

        with open(self.path_to_links, encoding="utf-8") as f:
            lines = f.readlines()

        links_header = parse_line(lines[0])
        links = [
            dict(zip(links_header, parse_line(line)))
            for line in lines[1:limit + 1]
        ]

        with open(self.path_to_movies, encoding="utf-8") as f:
            lines = f.readlines()

        movies_header = parse_line(lines[0])
        movies = {
            row["movieId"]: {
                "title": row["title"],
                "genres": row["genres"],
            }
            for row in (
                dict(zip(movies_header, parse_line(line)))
                for line in lines[1:limit + 1]
            )
        }

        merged = []
        for row in links:
            movie_id = row["movieId"]

            merged_row = dict(row)
            if movie_id in movies:
                merged_row["title"] = movies[movie_id]["title"]
                merged_row["genres"] = movies[movie_id]["genres"]

            merged.append(merged_row)

        return merged

    def _load_cache(self, path: str) -> dict:
        """
        Загружает кэш из JSON-файла, если он существует.
        Аргументы: path: путь к файлу кэша
        Возвращает: словарь с кэшированными данными или пустой словарь
        """
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def _save_cache(self, cache: dict, path: str) -> None:
        """
        Атомарно сохраняет кэш в JSON-файл через временный файл.
        Аргументы:  cache: словарь с данными для сохранения
                    path: путь к файлу кэша
        """
        tmp_path = path + ".tmp"
        snapshot = dict(cache)
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(snapshot, f, ensure_ascii=False, indent=2)
        os.replace(tmp_path, path)

    def _get_id_for_movie(self, movie_id: str | int, source: str = "imdb") -> str:
        """
        Находит идентификатор фильма для указанного источника по movieId.
        Аргументы:  movie_id: идентификатор фильма из CSV
                    source: источник данных - "imdb" или "tmdb"
        Возвращает: строку с идентификатором для API
        """
        if source not in ("imdb", "tmdb"):
            raise ValueError(f"Invalid source '{source}'. Expected 'imdb' or 'tmdb'.")

        movie_id = str(movie_id)
        for row in self.data:
            if row["movieId"] == movie_id:
                if source == "imdb":
                    return "tt" + row["imdbId"].strip().zfill(7)
                if source == "tmdb":
                    return row["tmdbId"].strip()

        raise KeyError(f"movieId={movie_id} not found.")

    def _fetch_movie(self, api_id: str, source: str = "imdb") -> Optional[dict]:
        """
        Возвращает данные о фильме из кэша или делает запрос к API.
        Аргументы:  api_id: идентификатор фильма в API источника
                    source: источник данных - "imdb" или "tmdb"
        Возвращает: словарь с полями title, budget, gross, runtime, directors
                    или None если запрос не удался
        """
        if source not in ("imdb", "tmdb"):
            raise ValueError(f"Invalid source '{source}'. Expected 'imdb' or 'tmdb'.")

        cache = self._cache if source == "imdb" else self._tmdb_cache
        if api_id in cache:
            return cache[api_id]

        time.sleep(random.uniform(0.1, 0.3))

        try:
            if source == "imdb":
                data = self._request_imdb(api_id)
            else:
                data = self._request_tmdb(api_id)
        except requests.RequestException:
            cache[api_id] = None
            return None

        cache[api_id] = data
        return data

    def _request_imdb(self, imdb_id: str) -> Optional[dict]:
        """
        Выполняет GraphQL-запрос к IMDb API и возвращает данные о фильме.
        Аргументы:  imdb_id: идентификатор фильма в формате tt0000000
        Возвращает: словарь с полями title, budget, gross, runtime, directors
                    или None если данные не найдены
        """
        url = "https://api.graphql.imdb.com/"
        query = """
        query GetMovieData($id: ID!) {
          title(id: $id) {
            titleText { text }
            productionBudget { budget { amount currency } }
            lifetimeGross(boxOfficeArea: WORLDWIDE) { total { amount currency } }
            runtime { seconds }
            principalCredits {
              category { id }
              credits { name { nameText { text } } }
            }
          }
        }
        """
        try:
            r = requests.post(url, json={"query": query, "variables": {"id": imdb_id}}, timeout=15)
            r.raise_for_status()
        except requests.RequestException as e:
            raise requests.RequestException(f"IMDb request failed for {imdb_id}: {e}") from e

        data = r.json().get("data", {}).get("title", {})
        if not data:
            return None

        directors = []
        for section in data.get("principalCredits", []):
            if section.get("category", {}).get("id") == "director":
                for credit in section.get("credits", []):
                    name = credit.get("name", {}).get("nameText", {}).get("text")
                    if name:
                        directors.append(name)

        return {
            "title": (data.get("titleText") or {}).get("text", "N/A"),
            "budget": ((data.get("productionBudget") or {}).get("budget") or {}).get("amount", 0) or 0,
            "gross": ((data.get("lifetimeGross") or {}).get("total") or {}).get("amount", 0) or 0,
            "runtime": ((data.get("runtime") or {}).get("seconds") or 0) // 60,
            "directors": directors,
        }

    def _request_tmdb(self, tmdb_id: str) -> Optional[dict]:
        """
        Выполняет запрос к TMDB API и возвращает данные о фильме.
        Аргументы:  tmdb_id: идентификатор фильма в TMDB
        Возвращает: словарь с полями title, budget, gross, runtime, directors
                    или None если данные не найдены
        """
        api_key = os.environ.get("TMDB_API_KEY")
        if not api_key:
            raise EnvironmentError("TMDB_API_KEY environment variable is not set.")

        url = f"https://api.themoviedb.org/3/movie/{tmdb_id}"
        params = {"api_key": api_key, "append_to_response": "credits"}

        try:
            r = requests.get(url, params=params, timeout=15)
            r.raise_for_status()
        except requests.RequestException as e:
            raise requests.RequestException(f"TMDB request failed for {tmdb_id}: {e}") from e

        data = r.json()
        if not data:
            return None

        directors = []
        for member in data.get("credits", {}).get("crew", []):
            if member.get("job") == "Director":
                name = member.get("name")
                if name:
                    directors.append(name)

        return {
            "title": data.get("title", "N/A"),
            "budget": data.get("budget", 0) or 0,
            "gross": data.get("revenue", 0) or 0,
            "runtime": data.get("runtime", 0) or 0,
            "directors": directors,
        }

    def _field_value(self, movie_info: dict, field: str) -> str | int:
        """
        Извлекает значение нужного поля из словаря с данными о фильме.
        Аргументы:  movie_info: словарь с данными о фильме
                    field: название поля (director, budget, gross, runtime, title)
        Возвращает: значение поля или "N/A", если поле не распознано
        """
        field_lower = field.lower()
        if field_lower == "director":
            return ", ".join(movie_info["directors"]) if movie_info["directors"] else "N/A"
        if field_lower == "budget":
            return movie_info["budget"]
        if field_lower in ("cumulative worldwide gross", "gross", "revenue"):
            return movie_info["gross"]
        if field_lower == "runtime":
            return movie_info["runtime"]
        if field_lower == "title":
            return movie_info["title"]
        return "N/A"

    def _get_info(self, list_of_movies: list, list_of_fields: list, source: str = "imdb") -> list[list]:
        """
        Общий метод для получения данных о фильмах из IMDb или TMDB.
        Аргументы:  list_of_movies: список movieId
                    list_of_fields: список названий полей для извлечения
                    source: источник данных — "imdb" или "tmdb"
        Возвращает: список списков вида [movieId, field1, field2, ...],
                    отсортированный по movieId по убыванию
        """
        if source not in ("imdb", "tmdb"):
            raise ValueError(f"Invalid source '{source}'. Expected 'imdb' or 'tmdb'.")

        cache = self._cache if source == "imdb" else self._tmdb_cache
        cache_path = self._imdb_cache_path if source == "imdb" else self._tmdb_cache_path
        result = []
        for movie_id in list_of_movies:
            try:
                api_id = self._get_id_for_movie(movie_id, source)
                info = self._fetch_movie(api_id, source)
                if info is None:
                    continue
                row = [movie_id] + [self._field_value(info, f) for f in list_of_fields]
                result.append(row)
            except Exception as e:
                print(f"Ошибка при загрузке movieId={movie_id} из {source}: {e}")
                continue
        result.sort(key=lambda x: int(x[0]), reverse=True)
        self._save_cache(cache, cache_path)
        return result

    def _fetch_all(self) -> None:
        """
        Параллельно загружает данные по всем фильмам из self.data через IMDB API,
        пропуская уже кэшированные. После завершения сохраняет кэш на диск.
        """
        imdb_ids = []
        for row in self.data:
            try:
                iid = self._get_id_for_movie(row["movieId"], "imdb")
                imdb_ids.append(iid)
            except KeyError:
                continue

        uncached = [iid for iid in imdb_ids if iid not in self._cache]

        total = len(uncached)
        done = 0
        try:
            with ThreadPoolExecutor(max_workers=3) as executor:
                futures = {executor.submit(self._fetch_movie, iid, "imdb"): iid for iid in uncached}
                for future in as_completed(futures):
                    try:
                        future.result()
                    except Exception as e:
                        iid = futures[future]
                        print(f"Ошибка при загрузке {iid}: {e}")
                    done += 1
                    print(f"\r[{done}/{total}] загружено...", end="", flush=True)
            print()
        except KeyboardInterrupt:
            print("\nЗагрузка прервана пользователем. Сохранение кэша...")
        finally:
            self._save_cache(self._cache, self._imdb_cache_path)

    def get_imdb(self, list_of_movies: list, list_of_fields: list) -> list[list]:
        """
        Возвращает данные о фильмах из IMDB по списку movieId.
        Аргументы:  list_of_movies: список movieId
                    list_of_fields: список полей для извлечения (director, budget, gross, runtime, title)
        Возвращает: список списков вида [movieId, field1, field2, ...],
                    отсортированный по movieId по убыванию
        """
        return self._get_info(list_of_movies, list_of_fields, "imdb")

    def get_tmdb(self, list_of_movies: list, list_of_fields: list) -> list[list]:
        """
        Возвращает данные о фильмах из TMDB по списку movieId.
        Аргументы:  list_of_movies: список movieId
                    list_of_fields: список полей для извлечения (director, budget, gross, runtime, title)
        Возвращает: список списков вида [movieId, field1, field2, ...],
                    отсортированный по movieId по убыванию
        """
        return self._get_info(list_of_movies, list_of_fields, "tmdb")

    def top_directors(self, n: int) -> dict[str, int]:
        """
        Возвращает топ-n режиссёров по количеству фильмов в датасете.
        Аргументы:  n: количество режиссёров в результате
        Возвращает: словарь {имя режиссёра: количество фильмов},
                    отсортированный по убыванию количества
        """
        if n <= 0:
            raise ValueError(f"n must be a positive integer, got {n}.")
        self._fetch_all()
        counts = defaultdict(int)
        for movie_info in self._cache.values():
            if movie_info is None:
                continue
            for director in movie_info["directors"]:
                counts[director] += 1
        return dict(sorted(counts.items(), key=lambda x: x[1], reverse=True)[:n])

    def most_expensive(self, n: int) -> dict[str, int]:
        """
        Возвращает топ-n самых дорогих фильмов по бюджету.
        Аргументы:  n: количество фильмов в результате
        Возвращает: словарь {название фильма: бюджет},
                    отсортированный по убыванию бюджета
        """
        if n <= 0:
            raise ValueError(f"n must be a positive integer, got {n}.")
        self._fetch_all()
        budgets = {
            info["title"]: info["budget"]
            for info in self._cache.values()
            if info and info["budget"] > 0
        }
        return dict(sorted(budgets.items(), key=lambda x: x[1], reverse=True)[:n])

    def most_profitable(self, n: int) -> dict[str, int]:
        """
        Возвращает топ-n самых прибыльных фильмов по разнице между мировыми сборами и бюджетом.
        Аргументы:  n: количество фильмов в результате, должно быть положительным

        Возвращает: словарь {название фильма: прибыль},
                    отсортированный по убыванию прибыли
        """
        if n <= 0:
            raise ValueError(f"n must be a positive integer, got {n}.")
        self._fetch_all()
        profits = {
            info["title"]: info["gross"] - info["budget"]
            for info in self._cache.values()
            if info and info["budget"] > 0 and info["gross"] > 0
        }
        return dict(sorted(profits.items(), key=lambda x: x[1], reverse=True)[:n])

    def longest(self, n: int) -> dict[str, int]:
        """
        Возвращает топ-n самых длинных фильмов по хронометражу.
        Аргументы:  n: количество фильмов в результате, должно быть положительным
        Возвращает: словарь {название фильма: хронометраж в минутах},
                    отсортированный по убыванию хронометража
        """
        if n <= 0:
            raise ValueError(f"n must be a positive integer, got {n}.")
        self._fetch_all()
        runtimes = {
            info["title"]: info["runtime"]
            for info in self._cache.values()
            if info and info["runtime"] > 0
        }
        return dict(sorted(runtimes.items(), key=lambda x: x[1], reverse=True)[:n])

    def top_cost_per_minute(self, n: int) -> dict[str, float]:
        """
        Возвращает топ-n фильмов с наибольшей стоимостью одной минуты.
        Аргументы:  n: количество фильмов в результате, должно быть положительным
        Возвращает: словарь {название фильма: стоимость минуты},
                    отсортированный по убыванию стоимости
        """
        if n <= 0:
            raise ValueError(f"n must be a positive integer, got {n}.")
        self._fetch_all()
        costs = {
            info["title"]: round(info["budget"] / info["runtime"], 2)
            for info in self._cache.values()
            if info and info["budget"] > 0 and info["runtime"] > 0
        }
        return dict(sorted(costs.items(), key=lambda x: x[1], reverse=True)[:n])