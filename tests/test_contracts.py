from __future__ import annotations

import unittest

from agentic_content_system.scaffold import default_brand, default_edit_plan, default_project
from agentic_content_system.schemas import load_schema
from agentic_content_system.validation import validate_json


class ContractTests(unittest.TestCase):
    def test_scaffold_contracts_validate(self) -> None:
        brand = default_brand("test-brand", example="gustav")
        project = default_project("test-brand", brand)
        plan = default_edit_plan("test-brand")
        self.assertEqual([], validate_json(brand, load_schema("brand")))
        self.assertEqual([], validate_json(project, load_schema("content-project")))
        self.assertEqual([], validate_json(plan, load_schema("edit-plan")))

    def test_missing_disabled_reason_is_invalid(self) -> None:
        brand = default_brand("test-brand")
        brand["channels"][3]["reason"] = ""
        issues = validate_json(brand, load_schema("brand"))
        self.assertTrue(any("reason" in str(issue) for issue in issues))

    def test_relative_path_normalization_is_cross_platform(self) -> None:
        from agentic_content_system.paths import safe_relative_path

        self.assertEqual("sources/source.mp4", safe_relative_path(r"sources\source.mp4").as_posix())
        with self.assertRaises(Exception):
            safe_relative_path(r"..\outside.mp4")

    def test_schema_const_and_project_delivery_shape_are_enforced(self) -> None:
        const_schema = {"type": "string", "const": "expected"}
        self.assertTrue(validate_json("wrong", const_schema))

        project = default_project("test-brand", default_brand("test-brand", example="gustav"), example="gustav")
        project["delivery_intent"]["routes"][0].pop("timezone")
        issues = validate_json(project, load_schema("content-project"))
        self.assertTrue(any("does not match any allowed shape" in str(issue) for issue in issues))

    def test_caller_specific_fields_are_not_local_project_contract(self) -> None:
        project = default_project("test-brand", default_brand("test-brand"))
        project["space_ref"] = "aios://caller-space"
        issues = validate_json(project, load_schema("content-project"))
        self.assertTrue(any("additional property" in str(issue) for issue in issues))
