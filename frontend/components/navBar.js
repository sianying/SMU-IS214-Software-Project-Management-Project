export default Vue.component("nav-bar", {
    data: function() {
        return {
            currentPageLink: "",
            role: "",
            staffName: "",
            isTrainer: 0,
            isLearnerView: false,
            isActive: [],
            learnerDisabled: false,

            switchLink: "",
            learnerLink:"view-list-of-enrolled-courses.html",
            HRLink:"view-list-of-courses-HR.html",
            trainerLink:"view-list-of-assigned-courses.html",

            coursesLinks: [
                "view-list-of-courses-HR.html",
                "view-specific-course-HR.html",
            ],
            pendingRequestLink: "HR_view_requests.html",
            isActive: [],
        }
    },
    methods: {
        setSelectedNavLink() {
            // get the url of current page; if its from add new course, display success alert for course creation
            this.currentPageLink = window.location.href.split("/").at(-1);
            // isLearnerView is true
            if (this.isLearnerView){
                if (this.coursesLinks.includes(this.currentPageLink)) {
                    // enrollable courses
                    this.isActive = ["active", 0]
                } else {
                    // enrolled courses
                    this.isActive = [0, "active"]
                }
            // HR view
            } else {
                if (this.currentPageLink === this.pendingRequestLink) {
                    this.isActive = [0, "active"]
                } else {
                    // all courses page
                    this.isActive = ["active", 0]
                }
            }
            
        },
        setCurrentView() {
            if (this.isLearnerView) {
                if (this.role === "HR"){
                    return "Switch to HR"
                } else if (this.isTrainer === true){
                    return "Switch to Trainer"
                } else {
                    return "Learner View"
                }
            } else {
                if (this.role === "Engineer" && this.isTrainer === false){
                    return "Learner View"
                } else {
                    return "Switch to Learner"
                }
            }
        },
        setSwitchViewLink() {
            if (this.isLearnerView){
                if (this.role === "HR"){
                    this.switchLink = this.HRLink;
                } else if (this.isTrainer === true){
                    this.switchLink = this.trainerLink; 
                } else {
                    this.switchLink = "#";
                }
            } else{
                this.switchLink = this.learnerLink; 
            }
        }, 
        updateIsLearnerView() {
            if (this.isLearnerView){
                localStorage.setItem("isLearnerView", JSON.stringify(false));
            } else {
                localStorage.setItem("isLearnerView", JSON.stringify(true));
            }
        },
    },
    created: function() {
        //Retrieve Account Details from localstorage
        const accountDetails = JSON.parse(localStorage.getItem("accountDetails"));
        const isLearnerView = JSON.parse(localStorage.getItem("isLearnerView"));
        this.role = accountDetails.role;
        this.staffName = accountDetails.staff_name;
        this.isTrainer = accountDetails.isTrainer;
        this.isLearnerView = isLearnerView;

        this.setSelectedNavLink();
        this.setSwitchViewLink();

    },
    template: `<nav class="navbar navbar-expand-sm navbar-light bg-light d-flex justify-content-between">
                    <a class="navbar-brand m-0 mr-2" href="./home.html"  id="navlogo">ONE STOP LMS</a>
                    <div class="collapse navbar-collapse" id="navbarNav">
                        <div class="navbar-nav text-align-center">
                            <a class="nav-link" href="./home.html">Home</a>
                            <a v-if="role === 'HR' && !isLearnerView" :class="['nav-link', isActive[0]]" href="./view-list-of-courses-HR.html" >All Courses</a>
                            <a v-if="role === 'HR' && !isLearnerView" :class="['nav-link', isActive[1]]" href="HR_view_requests.html">Pending Requests</a>
                            <a v-if="isLearnerView" :class="['nav-link', isActive[0]]" href="./view-list-of-courses-HR.html" >Enrollable Courses</a>
                            <a v-if="isLearnerView" :class="['nav-link', isActive[1]]" href="./view-list-of-enrolled-courses.html">Courses Enrolled</a>
                            <a v-if="isTrainer && !isLearnerView" class="nav-link active" href="view-list-of-assigned-courses.html">Courses Assigned</a>
                        </div>
                    </div>
                    <div class="profile">
                        <a class="profileName d-flex justify-content-center" disabled>
                            <img src="./images/image_2021-09-29_17-14-02.png" id="profilelogo">
                            <span class="mt-1 ml-2">{{ staffName }}</span>
                        </a>
                        <a class="switch-view d-flex mt-2" :href="switchLink" @click="updateIsLearnerView">{{ setCurrentView() }}</a>
                    </div>
                </nav>`

})