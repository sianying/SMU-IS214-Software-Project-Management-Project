
        const section1 = new Object();
        section1.num = "Section 1";
        section1.name = "Introduction to Installation of Ink Printers";
        section1.description = "This is a description of a section";
        section1.materialNames = ["Introduction", "Video tutorial", "Overview of course", "quiz1"];
        section1.materialLinks = [1,2,3,4];
    
        
      
        const course = new Object();
        course.courseName = "Installation of Ink Printers";
        course.courseID = "IC111";
        course.description = "This is a wider card with supporting text below as a natural lead-in to additional content. This content is a little bit longer.";
        course.sections = [section1];

        sectionHtml = "";
        //document.getElementById("homebar").innerHTML = `<a href="www.youtube.com" style="color: #3C64B1;">Home</a>
        //  /   
        //  <a href="www.youtube.com" style="color: #3C64B1;">Courses</a>
        //   / <a href="www.youtube.com" style="color: #3C64B1;">${course.courseID}</a> / ${section1.num}`
        document.getElementById("courseName").innerHTML = section1.num + "<hr>"
        for (let i = 0; i < section1.materialLinks.length; i++) {
             sectionHtml += `<a href="${section1.materialLinks[i]}" style="color: #3C64B1;">${section1.materialNames[i]}</a>` + "<hr>"
        }   
        sectionHtml = sectionHtml.slice(0, sectionHtml.length - 4);
        document.getElementById("courseDescription").innerHTML = sectionHtml;
       
        

