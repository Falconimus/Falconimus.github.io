# Eartraining
#### Video Demo: https://www.youtube.com/watch?v=v7DmTHAop7M
#### Description: 
So what is Eartraining? Eartraining is a web-based application that is user to practice one´s hearing.
I used a flask setup, similar to the finance problem in problem Set 9, with a bunch of html templates, a sql database and so on.
So lets break down the different files and folders of this project.

#### **/static**
So inside /static we first of have the images folder, inside which are images of different notes on the scale, a playbutton and
a pausebutton. Next up inside the sounds folder are just a few piano sounds that I recorded that the application uses. 
Then we have Ear_listen.ico which is the icon of the website and finally styles.css which is the css file I used for this project.

### **/templates**
Inside the templates folder are all the different html files, I´ll start breaking them down one by one:

#### **layout.html**
This is just the layout page, which get included in all other pages. It displays the navbar and also includes the styles file, the icon
and displays the titel.

#### **Index.html**
So this is the Index page, that is beeing displayed once the user is logged in. It just contains some Information about the website
and stuff one needs to know in order to understand the exercises (like Intervals). 

#### **exercises.html**
So this page gets displayed when the user goes to the /exercises route. It is made so the user can select the exercise which he 
wants to do and it´s difficulty. Exercises include Absolute and Intervals, and Difficulties include Easy, Medium and hard.
Finally there is a submit button and depending on what the user selected he either goes to Absolute.html or to Intervals.html

#### **Absolute.html**
So this is the first exercise, basically a playbutton gets displayed and when the user clicks it a random note gets played. The 
user then has to select which note was played by hearing. The notes that can get played, depend on the difficulty on Hard the 
note-selection is higher than on easy. When the user clicks the submit button the answer gets submitted to /resultcheck.

#### **Intervals.html**
This page is made for the second exercise; Intervals. In this exercise 2 sounds get played, one after the other and then they
get played together. The user´s task is to recognize how big the Interval between the 2 sounds was, and in which direction it goes
(as of ascending, descending or in the case of both sounds being the same note, unison). When the submit button gets clicked, 
the selected answer gets submittd to /resulcheck.

#### **result.html**
The user gets to this page after submitting an answer in any of the exercises. Depending on the answer´s correctess either CORRECT! with
a green background or WRONG! with a red background is displayed and in case the result is wrong, the correct answer gets displayed. There
is also a "Next button" which the user can click in order to get to the next round of the exercise. The current streak of the user is also
displayed. 

#### **stats.html**
On this page stats of the user that is currently logged in get displayed. There is a table which has a row for each Exercise in all 
three difficulties and there are a few column; Streak highscore which displays the highest streak of correct answers submitted on 
a exercise, the Winrate (which gets calculated by diving the won rounds by the lost rounds, in case there are no losses yet, 
the Winrate gets displayed as perfect), the total amount of rounds played, the total wins, the total losses, and the Leaderboard position
(which is a rank comparing all registered users, given depending on Streak highscore and incase 2 users have the same highscored, also based on winrate).

#### **Leaderboard.html**
This gets displayed when the user goes to the /leaderboard route and here the user can select (in a dropdown menu) which of the different 
leaderboards he wants to see. A leaderboard is a table has a bunch of rows, one for each user who has atleast reached a streak of one, and
has several columns: A "User column" that displayed the name, a "highest streak" column which displays the highest reached streak, a 
"Winrate column" which displays the user´s winrate and finally his position on the leaderboard. 
The table´s rows are orded by leaderboard position.

#### **sounds.html**
Here the user can play any of the sounds in this program and can also listen to different Intervals. He must simply select the mode 
(Interval or Note), and then depending on the mode either just select a note or an Interval and a direction. 
When the user has finished selecting what he wants to hear, he can press the play-button and the given Interval or Note will be played.
The user also gets displayed what he is playing on a notescale.

#### **login.html**
Simply the login page. The user needs to input his Username and password in order to login, in case they don´t match or the user doesn´t 
input username or password, an error message gets displayed.

#### **register.html**
This contains the register page, where the user needs to input a username and a password which he needs to confirm. Incase something wasn´t 
input or input right, an error message will be displayed.

#### **deregister.html**
On this page the user can delete his account. In order to do this, he must input his username, his password and also confirm his password. 
I decided that the user has to confirm his password as another confirmation that he is sure he wants to delete his account. One cannot
deregister an account which isn´t currently logged in.

### **Eartraining.db**
This is the sql database which conains 2 tables: a user´s table for all the registered users (which has the following columns: id, username 
and hash) and a stats table which records the different stats for every user. Inside the stats table is the user_id, which references 
the users table, the username, the exercise, the difficulty, the winrate, the streak-highscore, the ammount of played rounds, the amount of
won rounds, the amount of lost rounds and the leaderboard position.

### **app.py**
This is the python file, which handles all the different routes, the session, and has functions like generate_leaderboards() which ranks 
the users in the database.
Lets break down all the different routes inside app.py:

#### **/deregister**
This is the route that render deregister.html and checks if the submitted username and password match, and also deletes the given account.

#### **/**
This is the index route, which just renders the index.html file.

#### **/sounds**
Just renders sounds.html

#### **/leaderboard**
When this route is accessed, python loads all the stats for users into a list, ordered by their rank which then gets submitted to 
leaderboard.html, everytime this route is accessed the correct leaderboard positions automaticcally get generated. 

#### **/exercises**
When the user gets here, the exercises.html file is displayed, when the user submitts the exercise and difficulty, the acording exercise
page is displayed.

#### **/register**
On this route, if the request-method is GET, the user gets register.html displayed, otherwise the submitted data is checked and if it´s 
allright, the account is added and the user is logged in.

#### **/logout**
Here the user is simply logged out.

#### **/stats** 
Gets the currently logged in user´s stats, and loads them on stats.html

#### **/login**
Just the login route, when the user gets here with GET, it render login.html when he gets here with POST veryfies the login details
and if they match a registered account, logs the user in and redirects him to the index page.

#### **/result**
Here the result page gets displayed, depending on answer with WRONG! or CORRECT!

#### **/resultcheck**
This route changes the user´s stats, depending on answer and also declares a few global variables that /result can then use. I had to 
implement this seperately from /result so users couldn´t cheat by simply reloading the result page and therefore getting free wins.

## Design choices
I decided to include the two main exercises Intervals and Absolute, because they seemed the most relevant to me, and also decided 
they should have different difficulties for more or less advanced users. The navigation bar design was inspired by the finance 
problem set, because it was very fitting for this application as well. 
I implemented the index page and the sounds page so users who don´t know enough about music theory could get some explanation 
and have a way to practice in /sounds. The /stats route was simply made so the user could see his progress after practicing. 
I implemente /leaderboards so that different users could compete and therefore motivate each other for practicing their ear.

## Why did I choose this project? 
Personally i study music theory in a music school, and therefore have to practice my hearing regularly for the exams, 
since i didn´t find any good and free software on the Internet for that, I decided this could be my final project 
which will hopefully remain useful to me and other people who study music theory in years to come. 
I hope you liked my final project, This was CS50!

