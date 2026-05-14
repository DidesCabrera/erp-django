from pathlib import Path

from django.test import SimpleTestCase


class FoodPickerBadgeStaticAssetsTests(SimpleTestCase):
    def test_food_item_renderer_includes_picker_badges(self):
        path = (
            Path(__file__).resolve().parents[1]
            / "static"
            / "notas"
            / "js"
            / "food_item_list.js"
        )

        content = path.read_text(encoding="utf-8")

        self.assertIn("picker-item-badges", content)
        self.assertIn("picker-item-badge--", content)
        self.assertIn("is_user_food", content)
        self.assertIn("is_global_food", content)
        self.assertIn("is_verified", content)
        self.assertIn("visibility === \"core\"", content)

    def test_food_picker_css_includes_badge_styles(self):
        path = (
            Path(__file__).resolve().parents[1]
            / "static"
            / "notas"
            / "css"
            / "components"
            / "food_picker.css"
        )

        content = path.read_text(encoding="utf-8")

        self.assertIn(".picker-item-badges", content)
        self.assertIn(".picker-item-badge", content)
        self.assertIn(".picker-item-badge--user", content)
        self.assertIn(".picker-item-badge--global", content)
        self.assertIn(".picker-item-badge--verified", content)
        self.assertIn(".picker-item-badge--core", content)