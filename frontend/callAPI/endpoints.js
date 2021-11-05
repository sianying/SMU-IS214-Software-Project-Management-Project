// File to call courses related APIs
// Naming conventions e.g. retrieveAllCourses(), createCourse(), updateCourse(), deleteCourse()
// e.g. API call using async/await

export const URL = "http://13.250.140.89:5000";

// =========== Retrieve APIs ===========

// Retrieve all courses
export async function retrieveAllCourses(URL) {
    try {
        const response = await fetch(`${URL}/courses`);
        if (response) {
            const result = await response.json();
            return result;
        }
    } catch(e) {
        const error = {
            "code": 404,
            "data": e
        }
        return error;
    }
    
}

// Retrieve Specific Course
export async function retrieveSpecificCourse(URL, courseId) {
    try {
        const response = await fetch(`${URL}/courses/${courseId}`);
        if (response) {
            const result = await response.json();
            return result;
        }
    } catch(e) {
        const error = {
            "code": 404,
            "data": e
        }
        return error;
    }
    
}

// Retrieve qualified trainers for a specific course
export async function retrieveQualifiedTrainers(URL, courseId) {
    try {
        const response = await fetch(`${URL}/courses/qualified/${courseId}`);
        if (response) {
            const result = await response.json();
            return result;
        }
    } catch(e) {
        const error = {
            "code": 404,
            "data": e
        }
        return error;
    }
    
}

// Retrieve all courses a trainer is assigned
export async function retrieveAssignedCoursesTrainer(URL, staffId) {
    try {
        const response = await fetch(`${URL}/courses/assigned/${staffId}`);
        if (response) {
            const result = await response.json();
            return result;
        }
    } catch(e) {
        const error = {
            "code": 404,
            "data": e
        }
        return error;
    }
    
}

// Retrieve Eligible Course
export async function retrieveEligibleCourses(URL, staffId) {
    try {
        const response = await fetch(`${URL}/courses/eligible/${staffId}`);
        if (response) {
            const result = await response.json();
            return result;
        }
    } catch(e) {
        const error = {
            "code": 404,
            "data": e
        }
        return error;
    }
    
}

// Retrieve all classes
export async function retrieveAllClasses(URL, courseId) {
    try {
        const response = await fetch(`${URL}/class/${courseId}`);
        if (response) {
            const result = await response.json();
            return result;
        }
        } catch(e) {
        const error = {
            "code": 404,
            "data": e
        }
        return error;
    }
    
}

// Retrieve assigned class
export async function retrieveAssignedClasses(URL, courseId, staffId) {
    try {
        const response = await fetch(`${URL}/class/assigned/${courseId}/${staffId}`);
        if (response) {
            const result = await response.json();
            return result;
        }
        } catch(e) {
        const error = {
            "code": 404,
            "data": e
        }
        return error;
    }
    
}

// Retrieve all sections from class id
export async function retrieveAllSectionsFromClass(URL, courseId, classId) {
    try {
        const response = await fetch(`${URL}/section/${courseId}/${classId}`);
        if (response) {
            const result = await response.json();
            return result;
        }
        } catch(e) {
        const error = {
            "code": 404,
            "data": e
        }
        return error;
    }
    
}

// Retrieve specific section using section id
export async function retrieveSpecificSection(URL, sectionId) {
    try {
        const response = await fetch(`${URL}/section/${sectionId}`);
        if (response) {
            const result = await response.json();
            return result;
        }
        } catch(e) {
        const error = {
            "code": 404,
            "data": e
        }
        return error;
    }
    
}

// Retrieve all quizzes by quiz id
export async function retrieveQuizById(URL, quizId) {
    try {
        const response = await fetch(`${URL}/quiz/${quizId}`);
        if (response) {
            const result = await response.json();
            return result;
        }
        } catch(e) {
        const error = {
            "code": 404,
            "data": e
        }
        return error;
    }
    
}

// Retrieve all quizzes by quiz id
export async function retrieveQuizBySection(URL, sectionId) {
    try {
        const response = await fetch(`${URL}/quiz/section/${sectionId}`);
        if (response) {
            const result = await response.json();
            return result;
        }
        } catch(e) {
        const error = {
            "code": 404,
            "data": e
        }
        return error;
    }
    
}

// Retrieve all attempts by quiz id and staff id
export async function retrieveAttemptsByLearner(URL, quizId, staffId){
    try {
        const response = await fetch(`${URL}/attempts/${quizId}/${staffId}`);
        if (response) {
            const result = await response.json();
            return result;
        }
    } catch(e) {
        const error = {
            "code": 404,
            "data": e
        }
        return error;
    }
}


// Retrieve all attempts by quiz id and staff id
export async function retrieveLearnerProgress(URL, staffId, courseId){
    try {
        const response = await fetch(`${URL}/progress/${staffId}/${courseId}`);
        if (response) {
            const result = await response.json();
            return result;
        }
    } catch(e) {
        const error = {
            "code": 404,
            "data": e
        }
        return error;
    }
}


// Retrieve specific staff
export async function retrieveSpecificStaff(URL, staffId){
    try {
        const response = await fetch(`${URL}/staff/${staffId}`);
        if (response) {
            const result = await response.json();
            return result;
        }
    } catch(e) {
        const error = {
            "code": 404,
            "data": e
        }
        return error;
    }
}


// ====== create ========
//Create course
export async function createCourse(URL, body) {
    try {
        const data = {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(body)
        }
        const response = await fetch(`${URL}/courses`, data)
        if (response) {
            const result = await response.json()
            return result;
        }
    } catch(e) {
        const error = {
            "code": 404,
            "data": e
        }
        return error;
    }
}

//Create quiz
export async function createQuiz(URL, body) {
    try {
        const data = {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(body)
        }
        const response = await fetch(`${URL}/quiz/create`, data)
        if (response) {
            const result = await response.json()
            return result;
        }
    } catch(e) {
        const error = {
            "code": 404,
            "data": e
        }
        return error;
    }
}


//Create Attempt
export async function createAttempt(URL, body){
    try{
        const data = {
            method: 'POST',
            headers: {
                'Content-Type': "application/json"
            },
            body: JSON.stringify(body)
        }

        const response = await fetch(`${URL}/attempts`, data)
        if(response){
            const result = await response.json()
            return result;
        }
    }catch(e){
        const error = {
            "code": 404,
            "data": e
        }
        return error;
    }
}


// const body = {
//     "course_id": course_id,
//     "start_datetime": start_datetime,
//     "end_datetime": end_datetime,
//     "class_size": class_size
// }
//Create Class
export async function createClass(URL, body){
    try{
        const data = {
            method: 'POST',
            headers: {
                'Content-Type': "application/json"
            },
            body: JSON.stringify(body)
        }

        const response = await fetch(`${URL}/class`, data)
        if(response){
            const result = await response.json()
            return result;
        }
    }catch(e){
        const error = {
            "code": 404,
            "data": e
        }
        return error;
    }
}

// const body = {
//     "course_id": course_id,
//     "class_id": class_id,
//     "section_name": section_name
// }
//Create Section
export async function createSection(URL, body){
    try{
        const data = {
            method: 'POST',
            headers: {
                'Content-Type': "application/json"
            },
            body: JSON.stringify(body)
        }

        const response = await fetch(`${URL}/section`, data)
        if(response){
            const result = await response.json()
            return result;
        }
    }catch(e){
        const error = {
            "code": 404,
            "data": e
        }
        return error;
    }
}


// const body = {
//     "file": file,
//     "section_id": section_id
// }
//Upload Material
export async function uploadMaterial(URL, body){
    try{
        const response = await fetch(`${URL}/materials/file`, body)
        if(response){
            const result = await response.json()
            return result;
        }
    }catch(e){
        const error = {
            "code": 404,
            "data": e
        }
        return error;
    }
}

//Upload Material
export async function uploadLink(URL, body){
    try{
        const data = {
            method: 'POST',
            headers: {
                'Content-Type': "application/json"
            },
            body: JSON.stringify(body)
        }
        console.log(data)
        const response = await fetch(`${URL}/materials/link`, data)
        if(response){
            const result = await response.json()
            return result;
        }
    }catch(e){
        const error = {
            "code": 404,
            "data": e
        }
        return error;
    }
}


// ====== Update ========

// const body = {
//     "staff_id": staff_id,
//     "course_id": course_id,
//     "class_id": class_id
// }
//Enroll Learners
export async function enrollLearners(URL, body) {
    try {
        const data = {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(body)
        }
        const response = await fetch(`${URL}/class/enroll`, data)
        if (response) {
            const result = await response.json()
            return result;
        }
    } catch(e) {
        const error = {
            "code": 404,
            "data": e
        }
        return error;
    }
}

// const body = {
//     "course_id": course_id,
//     "class_id": class_id,
//     "staff_id": staff_id
// }
//Assign Trainer
export async function assignTrainer(URL, body) {
    try {
        const data = {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(body)
        }
        const response = await fetch(`${URL}/class/trainer`, data)
        if (response) {
            const result = await response.json()
            return result;
        }
    } catch(e) {
        const error = {
            "code": 404,
            "data": e
        }
        return error;
    }
}

//Update Class
export async function updateClassDetails(URL, body) {
    try {
        const data = {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(body)
        }
        const response = await fetch(`${URL}/class/edit`, data)
        if (response) {
            const result = await response.json()
            return result;
        }
    } catch(e) {
        const error = {
            "code": 404,
            "data": e
        }
        return error;
    }
}


//Update Quiz
export async function updateQuiz(URL, body) {
    try {
        const data = {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(body)
        }
        const response = await fetch(`${URL}/quiz/update`, data)
        if (response) {
            const result = await response.json()
            return result;
        }
    } catch(e) {
        const error = {
            "code": 404,
            "data": e
        }
        return error;
    }
}