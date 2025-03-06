from typing import Sequence
from pydantic import BaseModel
from tools.llm_configuration import DefaultLLMConfiguration as Configuration

configuration = Configuration()

class SubjectMark(BaseModel):
    """Marks for Each Subject."""
    subject: str
    """Subject name"""
    mark: int
    """Marks out of 100"""

class Student(BaseModel):
    """Student Details"""
    name: str
    """Name of the student"""
    subject_marks: list[SubjectMark]
    """List of Subject Marks"""

class Result(BaseModel):
    """Class Result of Each Student."""
    students: Sequence[Student]
    """List of students and details in the class."""

llm = configuration.get_llm(temperature=0).with_structured_output(Result)

result = llm.invoke("""Generate a JSON response for a class of 5 students Jacob, Peter, Thomas, Edan, Marco each having marks in 'maths', 'english', and 'science' out of 100.

Ensure the format matches this structure:
{
  "students": [
    {
      "name": "John Doe",
      "subject_marks": [
        {"subject": "maths", "mark": 85},
        {"subject": "english", "mark": 90},
        {"subject": "science", "mark": 78}
      ]
    },
    {
      "name": "Jane Doe",
      "subject_marks": [
        {"subject": "maths", "mark": 92},
        {"subject": "english", "mark": 88},
        {"subject": "science", "mark": 80}
      ]
    }
  ]
}
""")

class_result: Result = result
for c in class_result.students:
    print(c)