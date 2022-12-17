from canvasapi import Canvas

# Canvas API URL
_API_URL = "https://canvas.instructure.com/"

def test_key(api_key):
    """Tests Canvas API key
        Will throw InvalidAccessToken exception if invalid"""
    canvas = Canvas(_API_URL, api_key)
    canvas.get_current_user()


def list_assignments(course):
    """Returns list of public assignments for course
        Returns null if no assignments found"""

    assignments = list()

    for assignment in course.get_assignments():
        assignments.append(str(assignment))

    return assignments


def list_courses(api_key):
    """Returns list of courses for current user
        Returns null if no courses found"""

    canvas = Canvas(_API_URL, api_key)
    user = canvas.get_current_user()
    courses = list()

    for course in user.get_courses():
        courses.append(course.name)

    return courses


def search_course(api_key, query):
    """Returns first instance of course matching course_name
        Returns null if query is not found"""

    canvas = Canvas(_API_URL, api_key)
    user = canvas.get_current_user()

    courses = list()

    for course in user.get_courses():
        if query.lower() in str(course.name).lower():
            courses.append(course)

    return 