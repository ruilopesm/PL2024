from enum import Enum
from io import TextIOWrapper
from typing import Optional, Tuple
import sys
import re

def maybe_match_markdown_title(line: str) -> Optional[Tuple[str, int]]:
    """
    Return a tuple containing the content of the title and its level if the line is a valid Markdown title.
    Otherwise, return None.
    """
    match = re.match(r"^(#+)(.+)$", line)
    return (match.group(2).strip(), len(match.group(1))) if match else None

def create_html_header(content: str, level: int) -> str:
    """Create an HTML header of the given level with the given content inside."""
    return f"<h{level}>{content}</h{level}>"

def maybe_match_markdown_bold(line: str) -> Optional[str]:
    """
    Return the content of the bold if the line is a valid Markdown bold.
    Otherwise, return None.
    """
    match = re.match(r"^(\*\*|__)([^\*]*?)\1$", line)
    return match.group(2).strip() if match else None

def create_html_bold(content: str) -> str:
    """Create an HTML bold tag with the given content inside."""
    return f"<b>{content}</b>"

def maybe_match_markdown_italic(line: str) -> Optional[str]:
    """
    Return the content of the italic if the line is a valid Markdown italic.
    Otherwise, return None.
    """
    match = re.match(r"^(\*|_)([^*]*?)\1$", line)
    return match.group(2).strip() if match else None

def create_html_italic(content: str) -> str:
    """Create an HTML italic tag with the given content inside."""
    return f"<i>{content}</i>"

def maybe_match_markdown_image(line: str) -> Optional[Tuple[str, str]]:
    """
    Return a tuple containing the content and the URL of the image if the line is a valid Markdown image.
    Otherwise, return None.
    """
    match = re.match(r"!\[([^\]]+)\]\(([^)]+)\)", line)
    return (match.group(1), match.group(2)) if match else None

def create_html_image(content: str, url: str) -> str:
    """Create an HTML image tag with the given content and URL."""
    return f'<img src="{url}" alt="{content}">'

def maybe_match_markdown_link(line: str) -> Optional[Tuple[str, str]]:
    """
    Return a tuple containing the content and the URL of the link if the line is a valid Markdown link.
    Otherwise, return None.
    """
    match = re.match(r"\[([^\]]+)\]\(([^)]+)\)", line)
    return (match.group(1), match.group(2)) if match else None

def create_html_link(content: str, url: str) -> str:
    """Create an HTML link tag with the given content and URL."""
    return f'<a href="{url}">{content}</a>'

class MarkdownListType(Enum):
    ORDERED = 1
    UNORDERED = 2

def maybe_match_markdown_list_item(line: str) -> Optional[Tuple[str, MarkdownListType]]:
    """
    Return the content of the list item and the type of the list if the line is a valid Markdown list item.
    Otherwise, return None.
    """
    match = re.match(r"^(\d+\.|[*+-]) (.+)$", line)
    if match:
        if match.group(1)[:-1].isdigit(): # Number without the dot
            return (match.group(2), MarkdownListType.ORDERED)
        elif match.group(1) in ("*", "+", "-"):
            return (match.group(2), MarkdownListType.UNORDERED)
        
    return None

def create_html_start_list(list_type: MarkdownListType) -> str:
    """Create an HTML start list tag with the given type."""
    return "<ul>" if list_type == MarkdownListType.UNORDERED else "<ol>"

def create_html_end_list(list_type: MarkdownListType) -> str:
    """Create an HTML end list tag with the given type."""
    return "</ul>" if list_type == MarkdownListType.UNORDERED else "</ol>"

def create_html_list_item(content: str) -> str:
    """Create an HTML list item tag with the given content and type."""
    return f"<li>{content}</li>"

class ArgsType(Enum):
    FLAT = 1,
    BOTH = 2,
    FIRST = 3

def process_markdown_line(line: str, html: str, inside_list: Tuple[bool, MarkdownListType]) -> Tuple[str, Tuple[bool, MarkdownListType]]:
    """Process a Markdown line."""
    markdown_functions = [
        (maybe_match_markdown_title, create_html_header, ArgsType.BOTH),
        (maybe_match_markdown_bold, create_html_bold, ArgsType.FLAT),
        (maybe_match_markdown_italic, create_html_italic, ArgsType.FLAT),
        (maybe_match_markdown_image, create_html_image, ArgsType.BOTH),
        (maybe_match_markdown_link, create_html_link, ArgsType.BOTH),
        (maybe_match_markdown_list_item, create_html_list_item, ArgsType.FIRST)
    ]

    any_match: bool = False
    for markdown_function, html_function, args_type in markdown_functions:
        match = markdown_function(line)
        if match:
            any_match = True
            if args_type == ArgsType.FLAT:
                new_html = html_function(match)
            elif args_type == ArgsType.BOTH:
                new_html = html_function(*match)
            elif args_type == ArgsType.FIRST:
                new_html = html_function(match[0])

            if inside_list[0] and html_function != create_html_list_item:
                new_html = create_html_end_list(inside_list[1]) + new_html
                inside_list = (False, None)
            
            if not inside_list[0] and html_function == create_html_list_item:
                inside_list = (True, match[1])
                new_html = create_html_start_list(match[1]) + new_html

            if inside_list[0] and html_function == create_html_list_item and inside_list[1] != match[1]:
                new_html = create_html_end_list(inside_list[1]) + new_html
                new_html = create_html_start_list(match[1]) + new_html
                inside_list = (True, match[1])

            return (html + new_html, inside_list)
        
    if not any_match:
        html += line
        
    return (html, inside_list)

def main(stdin: TextIOWrapper) -> None:
    html: str = ""
    inside_list: Tuple[bool, MarkdownListType] = (False, None)

    for line in stdin:
        html, inside_list = process_markdown_line(line, html, inside_list)

    sys.stdout.write(html)

if __name__ == "__main__":
    main(sys.stdin)
