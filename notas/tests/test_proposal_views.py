from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from notas.domain.models import (
    DailyPlan,
    NutritionProposal,
)


class ProposalViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="felipe",
            email="felipe@example.com",
            password="pass123",
        )
        self.other_user = User.objects.create_user(
            username="other",
            email="other@example.com",
            password="pass123",
        )

        self.dailyplan = DailyPlan.objects.create(
            name="Training Day",
            created_by=self.user,
            is_public=False,
            is_draft=False,
        )
        self.other_dailyplan = DailyPlan.objects.create(
            name="Other Training Day",
            created_by=self.other_user,
            is_public=False,
            is_draft=False,
        )

        self.proposal = NutritionProposal.objects.create(
            dailyplan=self.dailyplan,
            created_by=self.user,
            source=NutritionProposal.SOURCE_AI,
            title="Increase protein",
            summary="Increase protein while keeping calories stable.",
            targets={
                "protein": 190,
            },
            current_snapshot={
                "dailyplan_id": self.dailyplan.id,
                "dailyplan_name": self.dailyplan.name,
                "actual": {
                    "protein": 170,
                },
            },
            proposed_payload={
                "intent": "adjust_dailyplan_to_targets",
                "suggested_changes": [],
            },
            validation_summary={
                "within_tolerance": False,
                "delta": {
                    "protein": -20,
                },
                "metrics": [
                    {
                        "metric": "protein",
                        "target": 190,
                        "actual": 170,
                        "delta": -20,
                        "tolerance": 10,
                        "within_tolerance": False,
                        "status": "under_target",
                    }
                ],
            },
        )

        self.other_proposal = NutritionProposal.objects.create(
            dailyplan=self.other_dailyplan,
            created_by=self.other_user,
            title="Private other proposal",
        )

    def test_proposal_list_requires_login(self):
        response = self.client.get(
            reverse("proposal_list"),
        )

        self.assertEqual(response.status_code, 302)

    def test_proposal_list_shows_visible_proposals_only(self):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse("proposal_list"),
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Increase protein")
        self.assertNotContains(response, "Private other proposal")

    def test_proposal_detail_shows_validation_data(self):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse(
                "proposal_detail",
                args=[self.proposal.id],
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Increase protein")
        self.assertContains(response, "Training Day")
        self.assertContains(response, "protein")
        self.assertContains(response, "-20")
        self.assertContains(response, "under_target")

    def test_proposal_detail_blocks_private_other_proposal(self):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse(
                "proposal_detail",
                args=[self.other_proposal.id],
            )
        )

        self.assertEqual(response.status_code, 404)

    def test_approve_proposal_marks_it_as_approved(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse(
                "proposal_approve",
                args=[self.proposal.id],
            )
        )

        self.assertEqual(response.status_code, 302)

        self.proposal.refresh_from_db()

        self.assertEqual(
            self.proposal.status,
            NutritionProposal.STATUS_APPROVED,
        )
        self.assertEqual(
            self.proposal.reviewed_by,
            self.user,
        )
        self.assertIsNotNone(self.proposal.reviewed_at)

        # Importante: aprobar todavía no modifica el DailyPlan.
        self.dailyplan.refresh_from_db()
        self.assertEqual(self.dailyplan.name, "Training Day")

    def test_reject_proposal_marks_it_as_rejected(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse(
                "proposal_reject",
                args=[self.proposal.id],
            )
        )

        self.assertEqual(response.status_code, 302)

        self.proposal.refresh_from_db()

        self.assertEqual(
            self.proposal.status,
            NutritionProposal.STATUS_REJECTED,
        )
        self.assertEqual(
            self.proposal.reviewed_by,
            self.user,
        )
        self.assertIsNotNone(self.proposal.reviewed_at)

    def test_cancel_proposal_marks_it_as_cancelled(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse(
                "proposal_cancel",
                args=[self.proposal.id],
            )
        )

        self.assertEqual(response.status_code, 302)

        self.proposal.refresh_from_db()

        self.assertEqual(
            self.proposal.status,
            NutritionProposal.STATUS_CANCELLED,
        )
        self.assertEqual(
            self.proposal.reviewed_by,
            self.user,
        )
        self.assertIsNotNone(self.proposal.reviewed_at)

    def test_unrelated_user_cannot_approve_private_proposal(self):
        self.client.force_login(self.other_user)

        response = self.client.post(
            reverse(
                "proposal_approve",
                args=[self.proposal.id],
            )
        )

        self.assertEqual(response.status_code, 404)

        self.proposal.refresh_from_db()

        self.assertEqual(
            self.proposal.status,
            NutritionProposal.STATUS_PENDING_REVIEW,
        )
