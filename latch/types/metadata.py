import json
import re
from dataclasses import dataclass, field, fields
from textwrap import dedent, indent
from typing import Any, List, Optional, Tuple

import yaml


@dataclass
class LatchRule:
    regex: str
    message: str

    @property
    def dict(self):
        return {"regex": self.regex, "message": self.message}

    def __post_init__(self):
        try:
            re.compile(self.regex)
        except re.error as e:
            raise ValueError(f"Malformed regex {self.regex}: {e.msg}")


@dataclass
class LatchParameter:
    display_name: Optional[str] = None
    description: Optional[str] = None
    hidden: bool = False
    section_title: Optional[str] = None
    placeholder: Optional[str] = None
    comment: Optional[str] = None
    output: bool = False
    batch_table_column: bool = False
    appearance_type: str = "line"
    rules: List[LatchRule] = field(default_factory=list)

    def __post_init__(self):
        if self.appearance_type not in ["line", "paragraph"]:
            raise ValueError(
                f'Invalid value passed to appearance type: "{self.appearance_type}" (must either be "line" or "paragraph")'
            )

    def __str__(self):
        metadata_yaml = yaml.dump(yaml.safe_load(json.dumps(self.dict)))
        return f"{self.description}\n{metadata_yaml}"

    @property
    def dict(self):
        parameter_dict = {"display_name": self.display_name}
        if self.output:
            parameter_dict["output"] = True
        if self.batch_table_column:
            parameter_dict["batch_table_column"] = True

        temp_dict = {"hidden": self.hidden}
        if self.section_title is not None:
            temp_dict["section_title"] = self.section_title
        parameter_dict["_tmp"] = temp_dict

        appearance_dict = {"type": self.appearance_type}
        if self.placeholder is not None:
            appearance_dict["placeholder"] = self.placeholder
        if self.comment is not None:
            appearance_dict["comment"] = self.comment
        parameter_dict["appearance"] = appearance_dict

        if len(self.rules) > 0:
            rules = []
            for rule in self.rules:
                rules.append(rule.dict)
            parameter_dict["rules"] = rules

        return {"__metadata__": parameter_dict}


@dataclass
class LatchMetadata:
    display_name: str
    documentation_link: Optional[str] = None
    name: Optional[str] = None
    email: Optional[str] = None
    github: Optional[str] = None
    repository: Optional[str] = None
    license: str = "MIT"
    parameters: dict[str, LatchParameter] = field(default_factory=dict)

    @property
    def dict(self):
        metadata_dict = {}
        sidebar_dict = {}
        sidebar_dict["display_name"] = self.display_name
        sidebar_dict["documentation"] = self.documentation_link
        sidebar_dict["author"] = {
            "name": self.name,
            "email": self.email,
            "github": self.github,
        }
        sidebar_dict["repository"] = self.repository
        sidebar_dict["license"] = {"id": self.license}
        metadata_dict["__metadata__"] = sidebar_dict

        return metadata_dict

    def __str__(self):
        def _parameter_str(t: Tuple[str, LatchParameter]):
            parameter_name, parameter_meta = t
            return f"{parameter_name}:\n" + indent(
                str(parameter_meta), "  ", lambda _: True
            )

        metadata_yaml = yaml.dump(yaml.safe_load(json.dumps(self.dict)))
        parameter_yaml = "\n".join(map(_parameter_str, self.parameters.items()))
        return (
            metadata_yaml + "Args:\n" + indent(parameter_yaml, "  ", lambda _: True)
        ).strip("\n ")
