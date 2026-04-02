from django.test import TestCase
from django.urls import reverse

from notas.presentation.config.viewmodel_config import DAILYPLAN_VIEWMODE_CONFIGURE
from notas.presentation.navigation.nav_builders import build_back_url


class NavigationBackConfigTests(TestCase):

    def test_build_back_url_uses_explicit_url_override(self):
        back_url = build_back_url(
            DAILYPLAN_VIEWMODE_CONFIGURE,
            back_config={
                "type": "url",
                "value": "/custom/edit-url/",
            },
        )

        self.assertEqual(back_url, "/custom/edit-url/")

    def test_build_back_url_uses_url_name_override(self):
        back_url = build_back_url(
            DAILYPLAN_VIEWMODE_CONFIGURE,
            back_config={
                "type": "url_name",
                "value": "dailyplan_create",
            },
        )

        self.assertEqual(back_url, reverse("dailyplan_create"))

    def test_build_back_url_returns_none_when_override_is_none(self):
        back_url = build_back_url(
            DAILYPLAN_VIEWMODE_CONFIGURE,
            back_config={
                "type": "none",
            },
        )

        self.assertIsNone(back_url)