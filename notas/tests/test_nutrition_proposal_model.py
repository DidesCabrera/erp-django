from django.contrib.auth.models import User
from django.test import TestCase

from notas.domain.models import (
    DailyPlan,
    NutritionProposal,
)


class NutritionProposalModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="felipe",
            email="felipe@example.com",
            password="pass123",
        )

        self.dailyplan = DailyPlan.objects.create(
            name="Training Day",
            created_by=self.user,
            is_public=False,
            is_draft=False,
        )

    def test_create_nutrition_proposal_with_minimum_required_fields(self):
        proposal = NutritionProposal.objects.create(
            dailyplan=self.dailyplan,
            created_by=self.user,
            title="Adjust Training Day",
            summary="Increase protein and slightly reduce carbs.",
            targets={
                "total_kcal": 2800,
                "protein": 190,
            },
            current_snapshot={
                "dailyplan_id": self.dailyplan.id,
                "total_kcal": 2600,
                "protein": 170,
            },
            proposed_payload={
                "intent": "adjust_dailyplan_to_targets",
                "suggested_changes": [],
            },
            validation_summary={
                "within_tolerance": False,
            },
        )

        self.assertEqual(proposal.dailyplan, self.dailyplan)
        self.assertEqual(proposal.created_by, self.user)
        self.assertEqual(
            proposal.status,
            NutritionProposal.STATUS_PENDING_REVIEW,
        )
        self.assertEqual(
            proposal.source,
            NutritionProposal.SOURCE_MANUAL,
        )
        self.assertTrue(proposal.is_reviewable)
        self.assertFalse(proposal.is_final)
        self.assertIsNone(proposal.reviewed_by)
        self.assertIsNone(proposal.reviewed_at)

    def test_nutrition_proposal_can_store_ai_source(self):
        proposal = NutritionProposal.objects.create(
            dailyplan=self.dailyplan,
            created_by=self.user,
            source=NutritionProposal.SOURCE_AI,
            title="AI protein adjustment",
            targets={
                "protein": 190,
            },
            proposed_payload={
                "intent": "adjust_dailyplan_to_targets",
                "agent": "ai",
            },
        )

        self.assertEqual(
            proposal.source,
            NutritionProposal.SOURCE_AI,
        )

    def test_nutrition_proposal_final_state_helpers(self):
        proposal = NutritionProposal.objects.create(
            dailyplan=self.dailyplan,
            created_by=self.user,
            title="Rejected proposal",
            status=NutritionProposal.STATUS_REJECTED,
        )

        self.assertFalse(proposal.is_reviewable)
        self.assertTrue(proposal.is_final)

    def test_nutrition_proposal_string_representation(self):
        proposal = NutritionProposal.objects.create(
            dailyplan=self.dailyplan,
            created_by=self.user,
            title="Adjust calories",
        )

        self.assertEqual(
            str(proposal),
            "Adjust calories (pending_review)",
        )


    def test_nutrition_proposal_applied_state_helpers(self):
        proposal = NutritionProposal.objects.create(
            dailyplan=self.dailyplan,
            created_by=self.user,
            title="Applied proposal",
            status=NutritionProposal.STATUS_APPLIED,
        )

        self.assertFalse(proposal.is_reviewable)
        self.assertTrue(proposal.is_final)