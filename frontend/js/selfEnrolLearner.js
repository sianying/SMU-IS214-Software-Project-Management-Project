
        const section1 = new Object();
        section1.num = "Section 1";
        section1.name = "Introduction to Installation of Ink Printers";
        section1.description = "This is a description of a section";
    
        const section2 = new Object();
        section2.num = "Section 2";
        section2.name = "How to install Ink Printers";
        section2.description = "This is a description of a section";
    
        const section3 = new Object();
        section3.num = "Section 3";
        section3.name = "Troubleshooting Ink Printers";
        section3.description = "This is a description of a section";
    
        const section4 = new Object();
        section4.num = "Section 4";
        section4.name = "Finding replacement parts";
        section4.description = "This is a description of a section";
      
        const course = new Object();
        course.courseName = "Installation of Ink Printers";
        course.courseID = "IC111";
        course.description = "This is a wider card with supporting text below as a natural lead-in to additional content. This content is a little bit longer.";
        course.sections = [section1,section2,section3,section4];

        const class1 = new Object();
        class1.num = "class 1";
        class1.availability = 15

        const class2 = new Object();
        class2.num = "class 2";
        class2.availability = 35

        const class3 = new Object();
        class3.num = "class 3";
        class3.availability = 5

        const classes = new Object();
        classes.class = [class1,class2,class3];


        sectionHtml = "";
        
        //document.getElementById("homebar").innerHTML = `<a href="www.youtube.com" style="color: #3C64B1;">Home</a>
        //  /   
        //  <a href="www.youtube.com" style="color: #3C64B1;">Courses</a>
         //  / ${course.courseID}`;

        
        document.getElementById("courseTitle").innerHTML = course.courseID + " " + course.courseName;
        
        document.getElementById("courseDescription").innerHTML = course.description;
        if(1 == 1){
          
          document.getElementById("enrolalert").innerHTML = `
                    You are eligible to enroll!
                  `
        }else{
          document.getElementById("enrolalert").classList.add('alert-danger');

          document.getElementById("enrolalert").classList.remove('alert-success');
          document.getElementById("enrolalert").innerHTML = `
                    You are not eligible to enroll!
                  `
        }
        document.getElementById("classes").innerHTML = `<a href="#" class="btn btn-primary btn-lg active" role="button" aria-pressed="true" id="availbutton" onclick="displayClass()">View Availability</a>`;
        document.getElementById("sectionName").innerHTML = `${section1.num} : ${section1.name} `;
        document.getElementById("sectionDescription").innerHTML = `${section1.description}`;
        for (let i = 1; i < course.sections.length; i++) {
             sectionHtml += "<li class='list-group-item'> " + course.sections[i].num + ": " + course.sections[i].name +"</li>";
        }   
        sectionHtml += "</ul>"
        document.getElementById("sectionList").innerHTML = sectionHtml;

        

        function displayClass(number) {
          classesHtml = "";
          for (let i = 0; i < classes.class.length; i++) {
             classesHtml += `<li class="list-group-item d-flex justify-content-between align-items-center">
                        ${classes.class[i].num}
                        <span class="badge badge-primary badge-pill">${classes.class[i].availability}</span>
                      </li>`
        }  
          document.getElementById("classes").innerHTML = `<div class="container" style="font-weight: 700;">
                    Class Availability
                  
                    <ul class="list-group">
                      <!--dynamically add classes-->
                      ${classesHtml}
                    </ul>
                    <ul></ul>
                    <div >
                      <div style = "float: right;"><button type="button" class="btn btn-secondary" onclick = "displayAvailable()">Close</button>
                        <a href="#" class="btn btn-primary  active mr-auto" role="button" aria-pressed="true" id="enrolbutton">Enrol</a>
                      </div>
                    
                  </div>
                  </div>
                `;
          
        }

        function displayAvailable(number) {
          document.getElementById("classes").innerHTML = `<a href="#" class="btn btn-primary btn-lg active" role="button" aria-pressed="true" id="availbutton" onclick="displayClass()">View Availability</a>`;
        }
     

       
      
        //var courseTitle = new Vue({
         // el: '#courseTitle',
         // data: {
          //  message: course.courseID + " " + course.courseName
         // }
        //})

        //var courseDescription = new Vue({
         // el: '#courseDescription',
          //data: {
            //message: course.description
//}
        //})
 
      

