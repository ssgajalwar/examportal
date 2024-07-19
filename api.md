# PROJECT DETAILS**
- Project Name - Exam Geek
- Application Name - ExamApp
- Developer Name - Shreenath Gajalwar

# API DOCUMENTATION**
- Page Name - This is the page title which will show on browser
- Path - Address in browser where page is rendered
- Name - page address stored in a variable which can accessed in entire application by its name
- Method - Whenever user hits the endpoint/url the sort of code which needs to be execute
- Parameters - the data required by the method 
- Requests -
-   :- GET - Used to fetch data from database
-   :- POST - Used to send data to database or to make some changes
-  Note - ( It is not mentioned anywhere specifically to use GET for fetching and POST for changing the data in database it is the common approch followed by developer's to accomplish there task's by segregating the responsibilities according to their behaviour)  
- context : The data we are passing to the client/user.basically it will go to the template and it will render that 
- Template - The file which will be executed whenever someone visits that url
- Return - the block of code which we are executing on visit of url what will it return
       

1.Home page
- Path : '/'
- Name : 'home'
- Method : home(request)
- parametes :  request
- Request : GET - Fetch All Exam data from *Exam Modal*
            POST - Fetch only query data from *Exam Modal*
- Template : home.html
- Context : exams
- Returns : render(request,template,context)

2.Exam - [Only Authenticated User Allowed]
- Path : 'exam/<int:exam_id>/'
- Name : 'exam'
- Method : exam(request,exam_id)
- parametes :  request,exam_id
- Request : GET - fetch first 25 questions of 'exam_id' from *Questions*
- Template : exam.html
- Context : questions,examname,exam_id,iterator
- Returns : when there are no questionns -> 
            HttpResponse(Message & link to Home)
            when there are questions -> 
            render(request,template,context)     
