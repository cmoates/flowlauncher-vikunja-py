"""
Natural language task parser for Vikunja
Supports both Vikunja and Todoist syntax styles
"""

import re
from datetime import datetime, timedelta
from typing import Dict, Any


class TaskParser:
    """Parses natural language task input"""

    # Parsing modes
    MODE_VIKUNJA = 'vikunja'
    MODE_TODOIST = 'todoist'

    def __init__(self):
        """Initialize the parser"""
        self.patterns = self._compile_patterns()

    def _compile_patterns(self) -> Dict[str, Any]:
        """Compile regex patterns for parsing"""
        return {
            # Vikunja style: +project *label !priority
            'vikunja_project': re.compile(r'\+(\w+)'),
            'vikunja_label': re.compile(r'\*([^\s]+)'),
            'vikunja_priority': re.compile(r'!([1-5])'),

            # Todoist style: #project @label p1-p5
            'todoist_project': re.compile(r'#(\w+)'),
            'todoist_label': re.compile(r'@([^\s]+)'),
            'todoist_priority': re.compile(r'p([1-5])'),
        }

    def parse(self, query: str, mode: str = MODE_VIKUNJA) -> Dict[str, Any]:
        """
        Parse a task query string

        Args:
            query: User's task input
            mode: Parsing mode ('vikunja' or 'todoist')

        Returns:
            Dictionary with parsed task components
        """
        if mode == self.MODE_TODOIST:
            return self._parse_todoist(query)
        else:
            return self._parse_vikunja(query)

    def _parse_vikunja(self, query: str) -> Dict[str, Any]:
        """Parse Vikunja format: task text +project *label !priority"""
        task = {
            'title': query,
            'description': '',
            'project': None,
            'labels': [],
            'priority': 0,
            'dueDate': None
        }

        # Extract project
        project_match = self.patterns['vikunja_project'].search(query)
        if project_match:
            task['project'] = project_match.group(1)
            query = self.patterns['vikunja_project'].sub('', query)

        # Extract labels
        label_matches = self.patterns['vikunja_label'].findall(query)
        if label_matches:
            task['labels'] = label_matches
            query = self.patterns['vikunja_label'].sub('', query)

        # Extract priority
        priority_match = self.patterns['vikunja_priority'].search(query)
        if priority_match:
            task['priority'] = int(priority_match.group(1))
            query = self.patterns['vikunja_priority'].sub('', query)

        # Extract due date and clean title
        task['title'], task['dueDate'] = self._extract_date(query.strip())

        return task

    def _parse_todoist(self, query: str) -> Dict[str, Any]:
        """Parse Todoist format: task text #project @label p1"""
        task = {
            'title': query,
            'description': '',
            'project': None,
            'labels': [],
            'priority': 0,
            'dueDate': None
        }

        # Extract project
        project_match = self.patterns['todoist_project'].search(query)
        if project_match:
            task['project'] = project_match.group(1)
            query = self.patterns['todoist_project'].sub('', query)

        # Extract labels
        label_matches = self.patterns['todoist_label'].findall(query)
        if label_matches:
            task['labels'] = label_matches
            query = self.patterns['todoist_label'].sub('', query)

        # Extract priority (Todoist uses p1-p5, map to Vikunja 1-5)
        priority_match = self.patterns['todoist_priority'].search(query)
        if priority_match:
            task['priority'] = int(priority_match.group(1))
            query = self.patterns['todoist_priority'].sub('', query)

        # Extract due date and clean title
        task['title'], task['dueDate'] = self._extract_date(query.strip())

        return task

    def _extract_date(self, text: str) -> tuple:
        """
        Extract due date from text using natural language patterns

        Returns:
            (cleaned_text, date_string) where date_string is ISO 8601 format or None
        """
        date_patterns = [
            (r'\btoday\b', 0),
            (r'\btomorrow\b', 1),
            (r'\bnext\s+week\b', 7),
            (r'\bnext\s+monday\b', self._days_until_monday),
            (r'\bmonday\b', self._days_until_monday),
            (r'\btuesday\b', self._days_until_weekday(1)),
            (r'\bwednesday\b', self._days_until_weekday(2)),
            (r'\bthursday\b', self._days_until_weekday(3)),
            (r'\bfriday\b', self._days_until_weekday(4)),
            (r'\bsaturday\b', self._days_until_weekday(5)),
            (r'\bsunday\b', self._days_until_weekday(6)),
            # ISO dates
            (r'\d{4}-\d{2}-\d{2}', 'iso'),
        ]

        for pattern, offset in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                text = re.sub(pattern, '', text, flags=re.IGNORECASE).strip()

                if offset == 'iso':
                    # Already ISO format
                    date_str = match.group(0)
                    return text, f"{date_str}T00:00:00.000Z"
                else:
                    # Calculate future date
                    if callable(offset):
                        days = offset()
                    else:
                        days = offset

                    future_date = datetime.now() + timedelta(days=days)
                    date_str = future_date.isoformat(timespec='milliseconds') + 'Z'
                    return text, date_str

        return text, None

    @staticmethod
    def _days_until_monday() -> int:
        """Calculate days until next Monday"""
        today = datetime.now().weekday()
        # Monday is 0, so next Monday is (7 - today) % 7 if today != 0 else 7
        return (7 - today) % 7 or 7

    @staticmethod
    def _days_until_weekday(target_weekday: int) -> callable:
        """Return function that calculates days until target weekday"""
        def calc():
            today = datetime.now().weekday()
            days = (target_weekday - today) % 7
            return days if days > 0 else 7
        return calc
