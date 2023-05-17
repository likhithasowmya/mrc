# mrc
When you run the project, a Tkinter window titled "Login/Signup Form" will appear. You can either log in with existing credentials or sign up as a new user. After successful login or signup, a new window titled "Home Page" will open.

In the "Home Page" window, you can enter a URL in the URL input field and click the "Upload URL" button. The program will scrape the content from the provided URL and display the first paragraph in the "content_label" text area.

You can then enter a question in the "question_entry" field and manually highlight the answer in the "content_label" text area. After highlighting the answer, you can click the "Get Indices" button to retrieve the starting and ending indices of the highlighted text. The indices will be displayed in the "start_index" and "end_index" fields.

You have the option to save the question along with the indices by clicking the "Save Question" button. If the question is successfully saved, a success message will be displayed; otherwise, an error message will be shown.

You can choose to ask another question for the same paragraph by clicking the "Yes" button, which will clear the question, starting index, and ending index fields. If you click the "No" button, the program will display the next paragraph, if available, in the "content_label" text area.

The program also includes session management, where sessions expire after 10 minutes of inactivity. If a session expires, the user will be prompted to log in again.
