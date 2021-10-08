// File to call courses related APIs
// Naming conventions e.g. retrieveAllCourses(), createCourse(), updateCourse(), deleteCourse()
// e.g. API call using async/await

export const URL = "http://127.0.0.1:5000";

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
        // alert("Error: No connection!");
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
        const response = await fetch(`${URL}/course/${courseId}`);
        if (response) {
            const result = await response.json();
            return result;
        }
    } catch(e) {
        alert("Error: No connection!");
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
        alert("Error: No connection!");
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
        alert("Error: No connection!");
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
        alert("Error: No connection!");
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
        alert("Error: No connection!");
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
        alert("Error: No connection!");
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
        alert("Error: No connection!");
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
        // alert("Error: No connection!");
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
        alert("Error: No connection!");
        const error = {
            "code": 404,
            "data": e
        }
        return error;
    }
}