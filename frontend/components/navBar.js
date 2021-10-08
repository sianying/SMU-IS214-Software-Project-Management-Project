export default Vue.component("nav-bar", {
    props: {
        homeLink: String,
        allCoursesLink: String,
        myCoursesLink: String
    },
    template: `<nav class="navbar navbar-expand-sm navbar-light bg-light">
                    <a class="navbar-brand" href="#"  id="navlogo">ONE STOP LMS</a>
                    <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
                        <span class="navbar-toggler-icon"></span>
                    </button>
                    <div class="collapse navbar-collapse" id="navbarNav">
                        <div class="navbar-nav">
                            <a class="nav-link" :href="homeLink || '#'">Home <span class="sr-only">(current)</span></a>
                            <a class="nav-link active" :href="allCoursesLink || '#'">All Courses</a>
                            <a class="nav-link" :href="myCoursesLink || '#'">My Courses</a>
                        </div>
                    </div>
                    <a class="nav-link" href="#"><img src="../images/image_2021-09-29_17-14-02.png" id="profilelogo"></a>
                </nav>`,
})