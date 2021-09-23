import json
class Course:
    def __init__(self, course_id, course_name, prerequisite_course = [],class_list = []):
        self.__course_id = course_name
        self.__course_name = course_name
        self.__class_list = class_list # stores a list of primary keys for the class objects
        self.__prerequisite_course = prerequisite_course # stores a list of primary keys for the course objects
    
    def get_course_id(self):
        return self.__course_id
    
    def get_course_name(self):
        return self.__course_name

    def get_class_list(self):
        return self.__class_list

    def get_prerequisite_course(self):
        return self.__prerequisite_course

    def add_class(self, class_object):
        self.__class_list.append(class_object)
        # add code to update object in dynamodb

    def add_prerequisite_course(self, course_obj_pri_key):
        self.__prerequisite_course.append(course_obj_pri_key)
        # add code to update object in dynamodb

