"""Tests for InMemoryTemplateStore."""

import pytest
from src.identity.models import FaceTemplate, UserProfile
from src.identity.template_store import InMemoryTemplateStore


class TestInMemoryTemplateStore:
    def test_add_and_get_user(self):
        store = InMemoryTemplateStore()
        profile = UserProfile(user_id="user_001", name="Alice")
        store.add_user(profile)
        assert store.get_user("user_001") == profile

    def test_get_user_not_found(self):
        store = InMemoryTemplateStore()
        assert store.get_user("user_999") is None

    def test_user_exists(self):
        store = InMemoryTemplateStore()
        store.add_user(UserProfile(user_id="user_001"))
        assert store.user_exists("user_001") is True
        assert store.user_exists("user_999") is False

    def test_add_and_get_template(self):
        store = InMemoryTemplateStore()
        template = FaceTemplate(
            template_id="tpl_001",
            user_id="user_001",
            embedding=[0.1, 0.2, 0.3],
        )
        store.add_template(template)
        assert store.get_template("tpl_001") == template

    def test_duplicate_template_raises(self):
        store = InMemoryTemplateStore()
        template = FaceTemplate(
            template_id="tpl_001",
            user_id="user_001",
            embedding=[0.1, 0.2, 0.3],
        )
        store.add_template(template)
        with pytest.raises(ValueError, match="already exists"):
            store.add_template(template)

    def test_get_templates_for_user(self):
        store = InMemoryTemplateStore()
        t1 = FaceTemplate(template_id="tpl_1", user_id="user_001", embedding=[0.1])
        t2 = FaceTemplate(template_id="tpl_2", user_id="user_001", embedding=[0.2])
        t3 = FaceTemplate(template_id="tpl_3", user_id="user_002", embedding=[0.3])
        store.add_template(t1)
        store.add_template(t2)
        store.add_template(t3)
        assert len(store.get_templates_for_user("user_001")) == 2
        assert len(store.get_templates_for_user("user_002")) == 1

    def test_get_all_templates(self):
        store = InMemoryTemplateStore()
        store.add_template(FaceTemplate("tpl_1", "user_001", [0.1]))
        store.add_template(FaceTemplate("tpl_2", "user_002", [0.2]))
        assert len(store.get_all_templates()) == 2

    def test_template_count(self):
        store = InMemoryTemplateStore()
        assert store.template_count() == 0
        store.add_template(FaceTemplate("tpl_1", "user_001", [0.1]))
        assert store.template_count() == 1

    def test_empty_templates_for_user(self):
        store = InMemoryTemplateStore()
        assert store.get_templates_for_user("user_001") == []
