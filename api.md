# PROJECT DETAILS
- Project Name - Exam Geek
- Application Name - ExamApp
- Developer Name - Shreenath Gajalwar

# API DOCUMENTATION
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
- Request : 
     - GET - Fetch All Exam data from *Exam Modal*
     - POST - Fetch only query data from *Exam Modal*
- Template : home.html
- Context : exams
- Returns : render(request,template,context)

2.Exam - [Only Authenticated User Allowed]
- Path : 'exam/<int:exam_id>/'
- Name : 'exam'
- Method : exam(request,exam_id)
- parametes :  request,exam_id
- Request : 
    - GET - fetch first 25 questions of 'exam_id' from *Questions*
    - POST - Send the Exam data to results page
- Template : exam.html
- Context : questions,examname,exam_id,iterator
- Returns : when there are no questionns -> 
            HttpResponse(Message & link to Home)
            when there are questions -> 
            render(request,template,context)     

3.Result - [Only Authenticated User Allowed]
- Path : 'exam/<int:exam_id>/result'
- Name : 'result'
- Method : result(request,exam_id)
- Parameters : reqquest,exam_id
- Request : 
    - GET - Check the Form and Orginal Data for correct answers and show that and calculate result
- Template : result.html
- Context : total_questions,correct_answers,exam,score
- Returns : render(request,template,context)

4.Register 
- Path : 'accounts/register/'
- Name : 'register'
- Method : register(request)
- Parameters : request
- Request : 
    - GET : Load the User Creation form
    - POST : Submit user creation form and save data (Create New User)
- Template : register.html 
- Context : form
- Returns : render(request,template,context)

5.Login
- Path : 'accounts/login/'
- Name : 'login'
- Method : user_login(request)
- Parameters : request
- Request : 
    - GET - Load the Login Form
    - POST - Check If user present and create a session
- Template : login.html
- Context : N/A
- Returns : render(request,template)

6.Logout
- Path : 'logout/'
- Name : logout
- Method : user_logout
- Parameters : request
- Request : 
    - GET - Logout the user
- Template : N/A 
- Context : N/A
- Returns : redirect('login')

7.Profile - [Only Authenticated User Allowed]
- Path : 'profile/'
- Name : profile
- Method : profile(request)
- Parameters : request 
- Request : 
    - POST - Update Profile
    - GET  - Fetch Exam History and Roadmap data 
- Template : profile.html
- Context : form,user_exam,roadmap,skillset
- Returns : render(request,template,context)

8.Dashboard - [Only Authenticated User Allowed]
- Path : 'dashboard/'
- Name : dashboard
- Method : dashboard(request)
- Parameters : request
- Request : 
    - GET - Fetch Graph data,Watched videos
- Template : dashoard.html
- Context : chart_data,watched_videos
- Returns : render(request,template,context)

9.Courses - [Only Authenticated User Allowed]
- Path : 'courses/'
- Name : courses
- Method : courses(request)
- Parameters : request
- Request : 
    - GET - Fetch the Videos 
- Template : courses.html
- Context : videos
- Returns : render(request,template,context)

10.Add Video - [Only Authenticated User Allowed]
- Path : 'add_video/'
- Name : 'add_video'
- Method :  add_video(request)
- Parameters : request
- Request : 
    - GET  - Load the Add Video Form
    - POST - Send the data to Database
- Template : add_video.html
- Context : form
- Returns : render(request,template,context)

11.Mark as Watched - [Only Authenticated User Allowed]
- Path : 'mark_as_watched/video_id'
- Name : 'mark_as_watched'
- Method : mark_as_wathced(request,video_id)
- Parameters : request,video_id
- Request : 
    - GET - Get video by id from YoutubeVideo, Update WatchedVideos
- Template : N/A
- Context : N/A
- Returns : redirect('courses') 

12.Roadmaps
- Path : 'roadmaps/'
- Name : 'roadmaps'
- Method : roadmaps(request)
- Parameters : request
- Request : 
    - POST - Get the name of roadmap from client and set that roadmap to RoadMap with user_id
    - GET - All roadmaps from the DB    
- Template : roadmaps.html
- Context : roadmapsdb
- Returns : render(request,template,context)

13.RoadMap Details
- Path : 'roadmaps/<str:profile>'
- Name : 'roadmap_detail'
- Method : roadmap_detail(request,profile)
- Parameters : request,profile
- Request : 
    - GET - Get all the skills related to that profile from RoadMapList
- Template : roadmap_details.html
- Context : profile,skills
- Returns : render(request,template,context) 