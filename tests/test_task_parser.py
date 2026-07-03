"""
Unit tests for task_parser module
"""

import pytest
from datetime import datetime, timedelta
from task_parser import TaskParser


class TestTaskParserVikunja:
    """Test Vikunja syntax parsing"""
    
    def setup_method(self):
        """Initialize parser for each test"""
        self.parser = TaskParser()
    
    def test_parse_simple_task_vikunja(self):
        """Test parsing simple task without modifiers"""
        result = self.parser.parse("Buy milk", mode="vikunja")
        assert result['title'] == "Buy milk"
        assert result['description'] == ""
        assert result['project'] is None
        assert result['labels'] == []
        assert result['priority'] == 0
    
    def test_parse_task_with_project_vikunja(self):
        """Test parsing task with +project modifier"""
        result = self.parser.parse("Buy milk +Shopping", mode="vikunja")
        assert result['title'] == "Buy milk"
        assert result['project'] == "Shopping"
    
    def test_parse_task_with_single_label_vikunja(self):
        """Test parsing task with *label modifier"""
        result = self.parser.parse("Buy milk *grocery", mode="vikunja")
        assert result['title'] == "Buy milk"
        assert "grocery" in result['labels']
    
    def test_parse_task_with_multiple_labels_vikunja(self):
        """Test parsing task with multiple *label modifiers"""
        result = self.parser.parse("Buy milk *grocery *urgent", mode="vikunja")
        assert result['title'] == "Buy milk"
        assert "grocery" in result['labels']
        assert "urgent" in result['labels']
    
    def test_parse_task_with_priority_vikunja(self):
        """Test parsing task with !priority modifier"""
        result = self.parser.parse("Buy milk !3", mode="vikunja")
        assert result['title'] == "Buy milk"
        assert result['priority'] == 3
    
    def test_parse_complex_task_vikunja(self):
        """Test parsing task with all modifiers"""
        result = self.parser.parse("Buy milk +Shopping *grocery *urgent !2", mode="vikunja")
        assert result['title'] == "Buy milk"
        assert result['project'] == "Shopping"
        assert "grocery" in result['labels']
        assert "urgent" in result['labels']
        assert result['priority'] == 2
    
    def test_parse_priority_range_vikunja(self):
        """Test priority values 1-5 are accepted"""
        for priority in range(1, 6):
            result = self.parser.parse(f"Task !{priority}", mode="vikunja")
            assert result['priority'] == priority
    
    def test_parse_invalid_priority_vikunja(self):
        """Test invalid priority is ignored"""
        result = self.parser.parse("Task !9", mode="vikunja")
        assert result['priority'] == 0


class TestTaskParserTodoist:
    """Test Todoist syntax parsing"""
    
    def setup_method(self):
        """Initialize parser for each test"""
        self.parser = TaskParser()
    
    def test_parse_simple_task_todoist(self):
        """Test parsing simple task without modifiers"""
        result = self.parser.parse("Buy milk", mode="todoist")
        assert result['title'] == "Buy milk"
        assert result['description'] == ""
        assert result['project'] is None
        assert result['labels'] == []
        assert result['priority'] == 0
    
    def test_parse_task_with_project_todoist(self):
        """Test parsing task with #project modifier"""
        result = self.parser.parse("Buy milk #Shopping", mode="todoist")
        assert result['title'] == "Buy milk"
        assert result['project'] == "Shopping"
    
    def test_parse_task_with_label_todoist(self):
        """Test parsing task with @label modifier"""
        result = self.parser.parse("Buy milk @grocery", mode="todoist")
        assert result['title'] == "Buy milk"
        assert "grocery" in result['labels']
    
    def test_parse_task_with_priority_todoist(self):
        """Test parsing task with p{1-4} modifier"""
        result = self.parser.parse("Buy milk p1", mode="todoist")
        assert result['title'] == "Buy milk"
        assert result['priority'] == 1  # p1 -> priority 1
        
        result = self.parser.parse("Buy milk p4", mode="todoist")
        assert result['priority'] == 4  # p4 -> priority 4
    
    def test_parse_complex_task_todoist(self):
        """Test parsing task with all modifiers"""
        result = self.parser.parse("Buy milk #Shopping @grocery @urgent p2", mode="todoist")
        assert result['title'] == "Buy milk"
        assert result['project'] == "Shopping"
        assert "grocery" in result['labels']
        assert "urgent" in result['labels']
        assert result['priority'] == 2  # p2 -> priority 2


class TestTaskParserDates:
    """Test date parsing functionality"""
    
    def setup_method(self):
        """Initialize parser for each test"""
        self.parser = TaskParser()
    
    def test_parse_today_date(self):
        """Test 'today' keyword"""
        result = self.parser.parse("Task today", mode="vikunja")
        today = datetime.now().date().isoformat()
        assert result['dueDate'].startswith(today)
        assert result['title'] == "Task"
    
    def test_parse_tomorrow_date(self):
        """Test 'tomorrow' keyword"""
        result = self.parser.parse("Task tomorrow", mode="vikunja")
        tomorrow = (datetime.now().date() + timedelta(days=1)).isoformat()
        assert result['dueDate'].startswith(tomorrow)
        assert result['title'] == "Task"
    
    def test_parse_next_week_date(self):
        """Test 'next week' keyword"""
        result = self.parser.parse("Task next week", mode="vikunja")
        next_week = (datetime.now().date() + timedelta(days=7)).isoformat()
        assert result['dueDate'].startswith(next_week)
        assert result['title'] == "Task"
    
    def test_parse_weekday_name_date(self):
        """Test weekday name (e.g., 'monday', 'friday')"""
        result = self.parser.parse("Task monday", mode="vikunja")
        # Should parse to next occurrence of Monday
        assert result['dueDate'] is not None
        assert result['title'] == "Task"
    
    def test_parse_iso_date(self):
        """Test ISO 8601 date format"""
        result = self.parser.parse("Task 2026-12-25", mode="vikunja")
        assert result['dueDate'].startswith("2026-12-25")
        assert result['title'] == "Task"
    
    def test_date_format_is_iso8601_with_milliseconds(self):
        """Test that dates are formatted as ISO 8601 with milliseconds"""
        result = self.parser.parse("Task today", mode="vikunja")
        # Format should be YYYY-MM-DDTHH:MM:SS.SSSZ
        assert "T" in result['dueDate']
        assert "Z" in result['dueDate']
        assert "." in result['dueDate']
    
    def test_parse_no_date(self):
        """Test task without date"""
        result = self.parser.parse("Task", mode="vikunja")
        assert result['dueDate'] is None
    
    def test_date_not_in_title(self):
        """Test that date keywords are removed from title"""
        result = self.parser.parse("Task today", mode="vikunja")
        assert result['title'] == "Task"
        
        result = self.parser.parse("Task tomorrow", mode="vikunja")
        assert result['title'] == "Task"


class TestTaskParserEdgeCases:
    """Test edge cases and boundary conditions"""
    
    def setup_method(self):
        """Initialize parser for each test"""
        self.parser = TaskParser()
    
    def test_empty_string(self):
        """Test parsing empty string"""
        result = self.parser.parse("", mode="vikunja")
        assert result['title'] == ""
    
    def test_task_with_multiple_spaces(self):
        """Test task with multiple spaces"""
        result = self.parser.parse("Buy  milk  +Project", mode="vikunja")
        # Title should contain task text
        assert "Buy" in result['title']
        assert "milk" in result['title']
    
    def test_case_insensitive_keywords_vikunja(self):
        """Test that modifiers work with any case"""
        result = self.parser.parse("Task +Project", mode="vikunja")
        assert result['project'] == "Project"
    
    def test_special_characters_in_task(self):
        """Test task with special characters"""
        result = self.parser.parse("Buy milk & bread +Shopping", mode="vikunja")
        assert "Buy milk & bread" in result['title']
    
    def test_unicode_characters(self):
        """Test task with unicode characters"""
        result = self.parser.parse("Acheter du lait +Épicerie", mode="vikunja")
        assert "Acheter" in result['title']
        assert result['project'] == "Épicerie"
    
    def test_default_mode_is_vikunja(self):
        """Test default parsing mode is vikunja"""
        result1 = self.parser.parse("Task +Project", mode="vikunja")
        result2 = self.parser.parse("Task +Project")
        assert result1 == result2
