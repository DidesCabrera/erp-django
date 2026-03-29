from notas.application.services.capabilities import get_capabilities
from notas.presentation.viewmodels.content.configure_vm import (
    ConfigureVM,
    ConfigureSectionUI,
    ConfigureFieldUI,
)
from notas.presentation.composition.viewmodel.builder_headers import build_dailyplan_header


def build_dailyplan_configure_vm(dailyplan, user, viewmode):

    caps = get_capabilities(user)

    header = build_dailyplan_header(
        dailyplan=dailyplan,
        user=user,
        context_name=viewmode,
    )

    sections = [

        ConfigureSectionUI(
            title="Visibility",
            fields=[
                ConfigureFieldUI(
                    name="is_public",
                    label="Share this daily plan in explore",
                    value=dailyplan.is_public,
                    enabled=caps.can_publish(),
                    hint="🔒 Publishing is available for nutritionists",
                )
            ],
        ),

        ConfigureSectionUI(
            title="Permissions",
            fields=[
                ConfigureFieldUI(
                    name="is_forkable",
                    label="Allow forks",
                    value=dailyplan.is_forkable,
                    enabled=True,
                ),

                ConfigureFieldUI(
                    name="is_copiable",
                    label="Allow copies",
                    value=dailyplan.is_copiable,
                    enabled=caps.can_copy(),
                    hint="🔒 Copies available on higher plans",
                ),
            ],
        ),

    ]

    return ConfigureVM(
        header=header,
        sections=sections,
    )