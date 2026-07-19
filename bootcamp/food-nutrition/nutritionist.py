#!/usr/bin/env python3
import sys
from recipes import RecipeAnalyzer


def main() -> None:
    
    CLASS_MESSAGES = {
        'bad': 'Мы бы не рекомендовали пробовать блюдо, совмещающее данные ингредиенты',
        'so-so': 'Возможно, вам не понравится это блюдо. А возможно понравится',
        'great': 'Мы настоятельно рекомендуем вам попробовать это блюдо',
    }

    if len(sys.argv) < 2:
        print("Использование: ./nutritionist.py ingredient1, ingredient2, ...")
        sys.exit(1)

    raw_input_str = " ".join(sys.argv[1:])
    ingredients_list = [ing.strip() for ing in raw_input_str.split(",") if ing.strip()]

    try:
        analyzer = RecipeAnalyzer()

        print("\nI НАШ ПРОГНОЗ")
        predicted_class = analyzer.predict_class(ingredients_list)
        print(f"Класс блюда: {predicted_class}")

        message = CLASS_MESSAGES.get(predicted_class)
        print(message)

        print("\nII ПИЩЕВАЯ ЦЕННОСТЬ ИНГРЕДИЕНТОВ")
        nutrition_facts = analyzer.get_nutrition_facts(ingredients_list)
        for ingredient, nutrients in nutrition_facts.items():
            print(f"\n{ingredient}:")
            for nutrient_name, value in nutrients.items():
                print(f"  {nutrient_name}: {value}%")

        print("\nIII ТОП-3 ПОХОЖИХ РЕЦЕПТА")
        similar_recipes = analyzer.get_similar_recipes(ingredients_list)
        for i, recipe in enumerate(similar_recipes, start=1):
            print(f"\n{i}. {recipe['title']}")
            print(f"   Рейтинг: {recipe['rating']}")
            print(f"   URL: {recipe['url']}")
            print(f"   Рецепт:\n{recipe['directions']}\n")

    except Exception as e:
        print(f"\nОшибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()