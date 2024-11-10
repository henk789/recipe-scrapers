from recipe_scrapers._grouping_utils import group_ingredients

from ._abstract import AbstractScraper
from ._utils import get_equipment, normalize_string


class Wprm(AbstractScraper):
    @classmethod
    def host(cls):
        return "veggie-einhorn.de"

    def ingredients(self):
        ingredient_tags = self.soup.find_all("li", class_="wprm-recipe-ingredient")

        ingredients_texts = []

        for ingredient_tag in ingredient_tags:
            # Find amount, unit, and name within each ingredient tag
            amount = ingredient_tag.find("span", class_="wprm-recipe-ingredient-amount")
            unit = ingredient_tag.find("span", class_="wprm-recipe-ingredient-unit")
            name = ingredient_tag.find("span", class_="wprm-recipe-ingredient-name")
            notes = ingredient_tag.find("span", class_="wprm-recipe-ingredient-notes")

            # Get text from each span, defaulting to an empty string if it's not found
            amount_text = amount.get_text().strip() if amount else ""
            unit_text = unit.get_text().strip() if unit else ""
            name_text = name.get_text().strip() if name else ""
            notes_text = notes.get_text().strip() if notes else ""

            # Combine extracted texts into a full ingredient description
            ingredient_text = f"{amount_text} {unit_text} {name_text}"
            if notes_text:
                notes_append = f" ({notes_text})"
                if notes_append.startswith(" ((") and notes_append.endswith("))"):
                    notes_append = notes_append.replace("((", "(").replace("))", ")")
                ingredient_text += notes_append
            ingredients_texts.append(normalize_string(ingredient_text.strip()))

        # print(ingredients_texts)

        return ingredients_texts

    def ingredient_groups(self):

        if len(self.soup.select(".wprm-recipe-ingredient-group")) > 0:
            return group_ingredients(
                self.ingredients(),
                self.soup,
                ".wprm-recipe-ingredient-group h4",
                ".wprm-recipe-ingredient",
            )
        elif len(self.soup.select(".recipe-ingredient-group")) > 0:
            return group_ingredients(
                self.ingredients(),
                self.soup,
                ".recipe-ingredient-group h3",
                ".wprm-recipe-ingredient",
            )

    def instructions(self):
        return "\n".join(self.instructions_list())

    def instructions_list(self):
        instructions = self.soup.findAll(
            "div",
            {"class": ["wprm-recipe-instruction-text", "recipe-instruction-text"]},
        )

        instructions_texts = []

        for instruction in instructions:
            spans = instruction.find_all(["span", "strong", "p"], recursive=False)

            if len(spans) > 0:
                instructions_texts.append(
                    "\n".join(
                        [normalize_string(span.get_text().strip()) for span in spans]
                    ).strip()
                )

            else:
                instructions_texts.append(
                    normalize_string(instruction.get_text().strip())
                )

        # print(instructions_texts)

        return instructions_texts

    def equipment(self):
        equipment_container = self.soup.select_one(".wprm-recipe-equipment-container")
        if not equipment_container:
            return None

        equipment_items = [
            item.get_text()
            for item in equipment_container.select(".wprm-recipe-equipment-name")
        ]
        return get_equipment(equipment_items)
