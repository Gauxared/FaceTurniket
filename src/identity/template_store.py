"""In-memory template store for user profiles and face templates."""

from typing import Dict, List, Optional

from src.identity.models import FaceTemplate, UserProfile


class InMemoryTemplateStore:
    """
    Local in-memory store for user profiles and face templates.

    Does not persist to disk. Suitable for MVP and testing.
    """

    def __init__(self):
        self._users: Dict[str, UserProfile] = {}
        self._templates: Dict[str, FaceTemplate] = {}
        self._user_templates: Dict[str, List[str]] = {}

    def add_user(self, profile: UserProfile) -> None:
        """Add or update a user profile."""
        self._users[profile.user_id] = profile

    def get_user(self, user_id: str) -> Optional[UserProfile]:
        """Find a user profile by id."""
        return self._users.get(user_id)

    def add_template(self, template: FaceTemplate) -> None:
        """Add a face template. Raises ValueError on duplicate template_id."""
        if template.template_id in self._templates:
            raise ValueError(
                f"Template with id '{template.template_id}' already exists"
            )
        self._templates[template.template_id] = template
        self._user_templates.setdefault(template.user_id, []).append(
            template.template_id
        )

    def get_template(self, template_id: str) -> Optional[FaceTemplate]:
        """Find a template by id."""
        return self._templates.get(template_id)

    def get_templates_for_user(self, user_id: str) -> List[FaceTemplate]:
        """List all templates for a given user."""
        template_ids = self._user_templates.get(user_id, [])
        return [self._templates[tid] for tid in template_ids]

    def get_all_templates(self) -> List[FaceTemplate]:
        """List all templates in the store."""
        return list(self._templates.values())

    def user_exists(self, user_id: str) -> bool:
        """Check if a user profile exists."""
        return user_id in self._users

    def template_count(self) -> int:
        """Total number of stored templates."""
        return len(self._templates)
