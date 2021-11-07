#Done by Chew Yong En Timothy
import unittest
import boto3
import sys
sys.path.append('../')
from moto import mock_dynamodb2

ITEM1= {
    "course_id": "IS111",
    "class_id" : 1,
    "staff_id" : "80e6f2f7-2827-4a3d-828a-0fdcea180641",
    "req_status" : "pending"
}

ITEM2 = {
    "course_id": "IS112",
    "class_id" : 1,
    "staff_id" : "aae3e316-af31-40ae-9540-0e3a401b20f6",
    "req_status" : "pending"
}

ITEM3 = {
    "course_id": "IS111",
    "class_id" : 1,
    "staff_id" : "aae3e316-af31-40ae-9540-0e3a401b20f6",
    "req_status" : "pending"
}



class TestCourse(unittest.TestCase):
    
    def setUp(self):
        from modules.request_manager import Request
        self.test_request = Request(ITEM1)
        
    def tearDown(self):
        self.test_request = None
        
    def test_update_req_status(self):
        from modules.request_manager import Request
        self.test_request = Request(ITEM2)
        with self.assertRaises(ValueError, msg = "Invalid status entered") as context:
            self.test_request.update_req_status("Reject")
        self.assertTrue("Status must be either approved or rejected" == str(context.exception))
        
        

    def test_json(self):
        self.assertTrue(isinstance(self.test_request.json(),dict), "Request JSON is not a dictionary object")
        self.assertEqual(ITEM1, self.test_request.json(), "Request does not match")
        self.assertNotEqual(ITEM2, self.test_request.json(), "Request matched when it should not")
        

@mock_dynamodb2
class TestRequestDAO(unittest.TestCase):

    def setUp(self):
        from modules import create_tables
        from modules.request_manager import RequestDAO 
        self.dynamodb = boto3.resource('dynamodb', region_name="ap-southeast-1")
        results = create_tables.create_request_table(self.dynamodb)
        # print(results)
        self.table = self.dynamodb.Table('Request')
        self.table.put_item(Item = ITEM1)
        self.table.put_item(Item = ITEM2)
        self.table.put_item(Item = ITEM3)
        self.dao = RequestDAO()
        
        

    def tearDown(self):
        self.dao = None
        self.table.delete()
        self.table = None
        self.dynamodb = None

    def test_insert_request_w_dict(self):
        
        insertTest = self.dao.insert_request_w_dict(ITEM3)
        self.assertEqual(ITEM3, insertTest.json(), "RequestDAO insert test with dictionary failure")
        
    def test_retrieve_all_pending(self):
        request_list = self.dao.retrieve_all_pending()
        self.assertEqual([ITEM1, ITEM2, ITEM3], [request.json() for request in request_list], "Retrieved list does not match")
        

    def test_retrieve_all_from_staff(self):
        request_list = self.dao.retrieve_all_from_staff("aae3e316-af31-40ae-9540-0e3a401b20f6")
        self.assertEqual([ITEM2, ITEM3], [request.json() for request in request_list], "Retrieved list does not match")

    def test_update_course(self):
        from modules.request_manager import Request
        requestObj = Request(ITEM1)
        requestObj.update_req_status("approved")
        self.dao.update_request(requestObj)
        toCheck = self.table.get_item(Key={'course_id':requestObj.get_course_id(), 'staff_id':requestObj.get_staff_id()})['Item']
        self.assertEqual(requestObj.json(), toCheck, "CourseDAO update test failure")


    
        



if __name__ == "__main__":
    unittest.main()