export default Vue.component("nav-bar", {
    data: function() {
        return {
            currentPageLink: "",
            role: "",
            staffName: "",
            isActive: []
        }
    },
    created: function() {
        //Retrieve Account Details from localstorage
        const accountDetails = JSON.parse(localStorage.getItem("accountDetails"));
        this.role = accountDetails.role;
        this.staffName = accountDetails.staff_name;
        // this.role = "Engineer";
        // this.staffName = "Tom";


        // get the url of current page; if its from add new course, display success alert for course creation
        this.currentPageLink = window.location.href.split("/").at(-1);
        if (this.currentPageLink === "view-list-of-courses-HR.html") {
            this.isActive = ["active", 0, 0]
        } else if (this.currentPageLink === "view-list-of-enrolled-courses.html") {
            this.isActive = [0, "active", 0]
        } else {
            this.isActive = [0, 0, "active"]
        }

    },
    template: `<nav class="navbar navbar-expand-sm navbar-light bg-light">
                    <a class="navbar-brand m-0 mr-2" href="./home.html"  id="navlogo">ONE STOP LMS</a>
                    <div class="collapse navbar-collapse" id="navbarNav">
                        <div class="navbar-nav">
                            <a class="nav-link" href="./home.html">Home</a>
                            <a :class="['nav-link', isActive[0]]" href="./view-list-of-courses-HR.html" >Courses</a>
                            <a :class="['nav-link', isActive[1]]" href="./view-list-of-enrolled-courses.html">Enrolled Courses</a>
                            <a v-if="role === 'Trainer'" :class="['nav-link', isActive[2]]" href="#">Assigned Courses</a>
                        </div>
                    </div>
                    <div class="navbar-nav">
                        <a class="nav-link" href="#">
                            <img src="./images/image_2021-09-29_17-14-02.png" id="profilelogo">
                            <span class="profileName">{{ role }}</span>
                        </a>
                    </div>
                </nav>`

})