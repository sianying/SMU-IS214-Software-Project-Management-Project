import boto3
import os
from boto3.dynamodb.conditions import Key
os.environ["AWS_SHARED_CREDENTIALS_FILE"] = "./aws_credentials"

dynamodb = boto3.resource('dynamodb')

# print(list(dynamodb.tables.all()))

def create_course(course_id, course_name, prerequisite_course = [], class_list = []):
    course = {
        "course_id": course_id,
        'course_name': course_name,
        'prerequisite_course': prerequisite_course,
        'class_list': class_list
    }

    response = dynamodb.Table("Course").put_item(
        Item = course
    )
    return response

def get_course(course_id):
    response = dynamodb.Table("Course").query(KeyConditionExpression = Key('course_id').eq(course_id))
    return response['Items']


if __name__ == '__main__':
    # create_course("IS111", "Intro to Programming", ["IS110","IS113"])
    print(get_course("IS111"))



# Sample format for objects in dynamodb
# Course Table
{
    "course_name": "Intro to Programming",
    "course_id": "IS111", # this is the course code must be unique 
    "prerequisite_course": ["IS110","IS113"], # this stores a list of course_id
    "class_list": [] # this stores a list of class_id
}
# Course Indexed By course_id (Partition Key), course_name(Sort Key)


# Class Table
{
    "class_id" : 1, # this must be a integer
    "course_id": "IS110", # this is the course code of the course the class belong to
    "start_datetime": "2021-08-21 08:00:00", # this should be a string version of the datetime object
    "end_datetime": "2021-10-21 23:59:59",
    "class_size": 20,
    "trainer_assigned": "<staff uuid here>",
    "learners_enrolled": ["bunch of staff uuid here"],
    "section_list": ["bunch of section_ids here"], # note the section id is a uuid so its most likely unique to help with indexing and retrieval
}
# Class Indexed by course_id (Partition Key), class_id(Sort Key)


# Section Table
{
    "section_id": "0a08ff5c-d72a-4207-b1de-9bbe99efa7fd", # this is generated with the uuid.uuid4() function in string format
    "section_name": "Paper Feeder",
    "course_id": "IS111", # course code of this section
    "class_id": 1, # class this section belongs to
    "materials":[ # contains a list of material objects
        {
            "mat_name": "Paper Feeder Chapter 1",
            "mat_type": "doc",
            "url" : "www.s3bucket.com"
        },
        {
            "mat_name": "Paper Feeder Chapter 2",
            "mat_type": "doc",
            "url" : "www.s3bucket.com"
        }
    ],
    "quiz_id": "e565b935-2adc-43b2-9d1c-c8fc29eee91a" # uuid of the quiz object
}
# Section indexed by section_id (Partition Key), class_id (Sort key)
# Section secondary index (CourseIndex) - course_id (Partition Key), class_id (Sort Key)

# Quiz Table
{
    "quiz_id": "e565b935-2adc-43b2-9d1c-c8fc29eee91a", # uuid to help with indexing
    "section_id": "0a08ff5c-d72a-4207-b1de-9bbe99efa7fd", #section id of which this quiz belongs to
    "questions":[ # contains a list of question objects
        {
            "question_no": 1,
            "isMCQ": False,
            "question_name": "Is this true?",
            "options":["True", "False"],
            "correct_option": 1, # 1 = index 1 
            "marks": 2
        },
        {
            "question_no": 2,
            "isMCQ": True,
            "question_name": "Is this true?",
            "options":["This is not true", "This is false", "idk"],
            "correct_option": 0,  
            "marks": 2
        }
    ]
}
# Quiz indexed by quiz_id (Partition Key), section_id (Sort key)
# Quiz secondary index (SectionIndex) - section_id (Partition key)

# Attempt Table
{
    "quiz_id": "e565b935-2adc-43b2-9d1c-c8fc29eee91a",
    "staff_id": "851252d7-b21c-4d75-95b6-321471ba3910",
    "attempt_id": 1,
    "options_selected": [1,1] # each element refers to the answer selected for each qn, so element at index 0 is question 1
}
# Attempt indexed by quiz_id (Partition Key), staff_id(Sort Key)


# Staff Table
{
    "staff_id": "851252d7-b21c-4d75-95b6-321471ba3910",
    "staff_name": "George",
    "courses_completed": ["IS110", "IS113"], # stores list of course_ids,
    "courses_enrolled": ["IS111"], #stores list of course_ids,
    "role": "Engineer"
}
# Staff indexed by staff_id (Partition Key), staff_name (Sort Key)
