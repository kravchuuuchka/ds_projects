import os
import joblib
import pandas as pd
import numpy as np
from typing import List, Dict, Any
import ast

class RecipeAnalyzer:
    """
    Основной класс для анализа рецептов.
    Загружает обученные модели и данные, предоставляет методы для предсказаний.
    """
    
    def __init__(self) -> None:
        """
        При создании объекта загружаем все готовые артефакты.
        """

        self.synonyms = {
            'milk': 'milk/cream',
            'green onion': 'green onion/scallion',
            'scallion': 'green onion/scallion',
            'sweet potato': 'sweet potato/yam',
            'yam': 'sweet potato/yam',
            'bread': 'breadcrumbs',
            'jelly': 'jam or jelly',
            'jam': 'jam or jelly',
        }

        BASE_DIR = os.path.dirname(os.path.abspath(__file__))


        required_files = {
            'feature_names': os.path.join(BASE_DIR, 'data', 'feature_names.pkl'),
            'class_model': os.path.join(BASE_DIR, 'data', 'best_classifier.pkl'),
            'urls_df': os.path.join(BASE_DIR, 'data', 'recipes_info.csv'),
            'nutrition_df': os.path.join(BASE_DIR, 'data', 'nutrition_facts.csv'),
            'recipes_df': os.path.join(BASE_DIR, 'data', 'clean_dataset.csv'),
        }

        for name, path in required_files.items():
            if not os.path.exists(path):
                raise FileNotFoundError(f"Не найден файл: {path}")

        self.feature_names = joblib.load(required_files['feature_names'])
        self.class_model = joblib.load(required_files['class_model'])
        self.urls_df = pd.read_csv(required_files['urls_df'])
        self.urls_df['title'] = self.urls_df['title'].str.strip()
        self.nutrition_df = pd.read_csv(required_files['nutrition_df'], index_col='Ingredient')
        self.recipes_df = pd.read_csv(required_files['recipes_df'])
        self.recipes_df = self.recipes_df[['title', 'rating'] + self.feature_names]
        self.recipes_df['title'] = self.recipes_df['title'].str.strip()

    def _prepare_features(self, ingredients_list: List[str]) -> pd.DataFrame:
        """
        Вспомогательный метод.
        Превращает список ингредиентов пользователя в DataFrame с бинарными признаками (0 и 1).
        """
        
        features = np.zeros(len(self.feature_names))
        
        for ing in ingredients_list:
            ing_lower = ing.lower().strip()
            
            if ing_lower in self.synonyms:
                ing_lower = self.synonyms[ing_lower]

            if ing_lower in self.feature_names:
                idx = self.feature_names.index(ing_lower)
                features[idx] = 1.0
            else:
                pass
                
        return pd.DataFrame([features], columns=self.feature_names)

    def predict_class(self, ingredients_list: List[str]) -> str:
        """
        Предсказывает класс блюда по списку ингредиентов.
        Возвращает строку: 'bad', 'so-so' или 'great'.
        """
        if not ingredients_list:
            raise ValueError("Список ингредиентов не может быть пустым")

        X = self._prepare_features(ingredients_list)

        if not bool(X.iloc[0].to_numpy(dtype=bool).any()):
            raise ValueError(
                "Ни один из введённых ингредиентов не найден в списке известных ингредиентов"
            )

        prediction = self.class_model.predict(X)[0]
        
        return prediction

    def get_nutrition_facts(self, ingredients_list: List[str]) -> Dict[str, Dict[str, float]]:
        """
        Возвращает словарь с нутриентами и их % DV для каждого ингредиента.
        Формат: {'Milk': {'Protein (% DV)': 6.0, 'Calcium (% DV)': 12.0, ...}, ...}
        """
        result: Dict[str, Dict[str, float]] = {}

        for ing in ingredients_list:
            ing_clean = ing.strip()
            ing_lower = ing_clean.lower()

            if ing_lower in self.synonyms:
                ing_lower = self.synonyms[ing_lower]

            match = None
            for idx_name in self.nutrition_df.index:
                if idx_name.lower() == ing_lower:
                    match = idx_name
                    break

            if match is None:
                continue

            row = self.nutrition_df.loc[match]

            nutrients: Dict[str, float] = {}
            for col in self.nutrition_df.columns:
                value = row[col]
                if pd.notna(value):
                    nutrients[col] = float(value)

            result[match] = nutrients

        if not result:
            raise ValueError(
                "Ни один из введённых ингредиентов не найден в базе данных нутриентов"
            )

        return result

    def get_similar_recipes(self, ingredients_list: List[str]) -> List[Dict[str, Any]]:
        """
        Находит top-3 наиболее похожих рецептов по коэффициенту Жаккара.
        Возвращает список словарей: [{'title': str, 'rating': float, 'url': str}, ...]
        """

        user_features_df = self._prepare_features(ingredients_list)
        user_vector = user_features_df.iloc[0].to_numpy(dtype=bool)

        if not bool(user_vector.any()):
            raise ValueError("Ни один из введённых ингредиентов не найден в списке известных ингредиентов")

        recipes_matrix = self.recipes_df[self.feature_names].values.astype(bool)

        intersection = np.logical_and(recipes_matrix, user_vector).sum(axis=1)
        union = np.logical_or(recipes_matrix, user_vector).sum(axis=1)

        with np.errstate(divide='ignore', invalid='ignore'):
            jaccard_scores = np.where(union > 0, intersection / union, 0.0)

        top_indices = np.argsort(jaccard_scores)[::-1][:3]

        result = []
        for i in top_indices:
            title = self.recipes_df.iloc[i]['title']
            rating = self.recipes_df.iloc[i]['rating']

            url_row = self.urls_df[self.urls_df['title'] == title]

            if not url_row.empty:
                url = url_row.iloc[0]['epicurious_url']
                directions = self._format_directions(url_row.iloc[0]['directions'])
            else:
                url = 'URL не найден'
                directions = 'Рецепт приготовления не найден'

            result.append({
                'title': title,
                'rating': float(rating) if pd.notna(rating) else None,
                'url': url,
                'directions': directions,
            })

        return result
    
    def _format_directions(self, raw_directions: Any) -> str:
        """
        Превращает строку вида "['1. Шаг один.', '2. Шаг два.']" в читаемый многострочный текст.
        """
        if pd.isna(raw_directions):
            return 'Рецепт приготовления не найден'

        try:
            steps = ast.literal_eval(raw_directions)
        except (ValueError, SyntaxError):
            return str(raw_directions).strip()

        if not isinstance(steps, list):
            return str(raw_directions).strip()

        return '\n'.join(str(step).strip() for step in steps)