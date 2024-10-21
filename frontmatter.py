import re
import yaml


class Frontmatter:
    """Frontmatter class to extract frontmatter from string."""

    _yaml_delim = r"(?:---|\+\+\+)"
    _yaml = r"(.*?)"
    _content = r"\s*(.+)$"
    _re_pattern = r"^\s*" + _yaml_delim + _yaml + _yaml_delim + _content
    _regex = re.compile(_re_pattern, re.S | re.M)

    @classmethod
    def read_file(cls, path):
        """Returns dict with separated frontmatter from file.

        Parameters
        ----------
        path : str
            The path to the file
        """
        with open(path, encoding="utf-8") as file:
            file_contents = file.read()
            return cls.read(file_contents)

    @classmethod
    def read(cls, string):
        """Returns dict with separated frontmatter from string.

        Parameters
        ----------
        string : str
            The string to extract frontmatter from


        Returns
        -------
        dict
            The separated frontmatter
        """
        fmatter = ""
        body = {}
        result = cls._regex.search(string)

        if result:
            fmatter = result.group(1)
            body_content = result.group(2)

            # Split the body content into sections
            sections = re.split(r"\n(?=\w+:)", body_content)
            for section in sections:
                if ":" in section:
                    key, value = section.split(":", 1)
                    body[key.strip()] = value.strip()
                else:
                    # If there's no colon, it's probably the first section (e.g., "system:")
                    body["system"] = section.strip()

        return {
            "attributes": yaml.load(fmatter, Loader=yaml.FullLoader),
            "body": body,
            "frontmatter": fmatter,
        }
