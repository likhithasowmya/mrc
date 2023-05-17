import tkinter as tk
import mysql.connector
import uuid
import time
import requests
from bs4 import BeautifulSoup

# Connect to MySQL database
db = mysql.connector.connect(
  host="localhost",
  user="root",
  password="sowmya@04J",
  database="miniproject"
)

# Create cursor object
cursor = db.cursor()
# Create users table if it doesn't exist
cursor.execute("CREATE TABLE IF NOT EXISTS users (id INT AUTO_INCREMENT PRIMARY KEY, username VARCHAR(255), password VARCHAR(255))")

# Create session ID table if it doesn't exist
cursor.execute("CREATE TABLE IF NOT EXISTS sessions ( id VARCHAR(36) PRIMARY KEY,  user_id INT, last_activity TIMESTAMP,FOREIGN KEY (user_id) REFERENCES users(id))")

# Create URL table if it doesn't exist
cursor.execute("CREATE TABLE IF NOT EXISTS urls (id VARCHAR(36) PRIMARY KEY, url VARCHAR(255), content TEXT, session_id VARCHAR(36), FOREIGN KEY (session_id) REFERENCES sessions(id))")

cursor.execute("CREATE TABLE IF NOT EXISTS questions (question VARCHAR(100) PRIMARY KEY, start_index INTEGER, end_index INTEGER, user_id INT, FOREIGN KEY (user_id) REFERENCES users(id))")


# Create Tkinter window
root = tk.Tk()
root.title("Login/Signup Form")
root.geometry("600x400")



bg_image = tk.PhotoImage(file="bluepink.png")
# Create a Label widget with the PhotoImage object as its background
bg_label = tk.Label(root, image=bg_image)
bg_label.place(relwidth=1, relheight=1)
# Create username and password input fields
username_label = tk.Label(root, text="Username",fg="blue")
username_label.pack()
username_entry = tk.Entry(root,bg="light yellow")
username_entry.pack()
password_label = tk.Label(root, text="Password",fg="blue")
password_label.pack()
password_entry = tk.Entry(root,bg="light yellow", show="*")
password_entry.pack()

# Create login button
def login():
    # Retrieve username and password inputs
    username = username_entry.get()
    password = password_entry.get()

    # Check if user exists in database
    cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
    user = cursor.fetchone()
    if user:
        # Check if session exists for user
        cursor.execute("SELECT * FROM sessions WHERE user_id=%s", (user[0],))
        session = cursor.fetchone()
        if session:
            # Check if session has expired
            session_id, user_id, last_activity = session
            expiration_time = 60 * 10 # session expires after 10 minutes of inactivity
            current_time = int(time.time())
            last_activity_time = int(last_activity.timestamp())
            if current_time - last_activity_time > expiration_time:
                # Delete expired session from database
                cursor.execute("DELETE FROM sessions WHERE id=%s", (session_id,))
                db.commit()
                # Prompt user to log in again
                error_label = tk.Label(root, text="Session expired. Please log in again.", fg="red")
                error_label.pack()
                return
        else:
            # Create new session ID and store in database
            session_id = str(uuid.uuid4())
            cursor.execute("INSERT INTO sessions (id, user_id, last_activity) VALUES (%s, %s, NOW())", (session_id, user[0]))
            db.commit()


        # Redirect to home page with session ID parameter
        root.destroy() # Destroy current window
        home_window = tk.Tk() # Create new window
        home_window.title("Home Page")
        home_window.geometry("1000x1000")
        home_window.configure(bg="light pink")
        home_label = tk.Label(home_window, text=f"Welcome, {user[1]}!")
        home_label.pack()

        # Create URL upload form
        url_label = tk.Label(home_window, text="Enter URL")
        url_label.pack()
        url_entry = tk.Entry(home_window,width=100,bg="light cyan")
        url_entry.pack()

        # Create URL upload button
        def upload_url():
            global paragraphs
            global current_paragraph_index
    
            # Retrieve URL input
            url = url_entry.get()

            # Scrape URL content
            response = requests.get(url)
            soup = BeautifulSoup(response.content, "html.parser")
            paragraphs = [p.text.strip() for p in soup.find_all('p')]
            current_paragraph_index = 0
            content = '\n\n'.join(paragraphs)
            first_paragraph = paragraphs[0]

    # Create new URL ID and store in database
            url_id = str(uuid.uuid4())
            cursor.execute("INSERT INTO urls (id, url, content, session_id) VALUES (%s, %s, %s, %s)", (url_id, url, content,session_id))

            db.commit()

    # Show first paragraph of content
            content_label.delete('1.0', tk.END) # clear existing content
            content_label.insert(tk.END, first_paragraph)   

        upload_button = tk.Button(home_window, text="Upload URL", command=upload_url)
        upload_button.pack()

        # Create content display label
        
        content_label = tk.Text(home_window, height=20, width=100,bg="light yellow")
        content_label.pack()
        
         # Create ask a question form
        question_label = tk.Label(home_window, text="Type your question:")
        question_label.pack()
        question_entry = tk.Entry(home_window,width=100,bg="light cyan")
        question_entry.pack()
       

        def get_indices():
            start = content_label.index("sel.first")
            end = content_label.index("sel.last")
            start_char = int(start.split(".")[1])
            end_char = int(end.split(".")[1])
            start_index.delete(0, tk.END)
            end_index.delete(0, tk.END)
            start_index.insert(0, start_char)
            end_index.insert(0, end_char)


        # create a button widget to get the indices of the highlighted text
        get_indices_button = tk.Button(home_window, text="Get Indices", command=get_indices,bg="light green")
        get_indices_button.pack(pady=(10,0))

        # create a label widget for the starting index
        start_index_label = tk.Label(home_window, text="Starting Index:")
        start_index_label.pack()

        # create an entry widget for the starting index
        start_index = tk.Entry(home_window,bg="light cyan")
        start_index.pack()

        # create a label widget for the ending index
        end_index_label = tk.Label(home_window, text="Ending Index:")
        end_index_label.pack()

        # create an entry widget for the ending index
        end_index = tk.Entry(home_window,bg="light cyan")  
        end_index.pack()
        # Create save button
        def save_question():
            # Retrieve question and highlighted answer inputs
            question = question_entry.get()
     
            # Retrieve starting and ending indices
            startindex = start_index.get()
            endindex = end_index.get()

            # Create new question entry in database
            try:
               cursor.execute("INSERT INTO questions (question, start_index, end_index, user_id) VALUES (%s, %s, %s, %s)", (question, startindex, endindex, user[0]))

               db.commit()
        # Show success message
               success_label = tk.Label(home_window, text="Question saved successfully!", fg="green")
               success_label.pack()
            except Exception as e:
               print("Error: ", e)
               db.rollback()
        # Show error message
               error_label = tk.Label(home_window, text="Error occurred while saving question. Please try again.", fg="red")
               error_label.pack()

        save_button = tk.Button(home_window, text="Save Question", command=save_question, bg="orange")
        save_button.pack(pady=(10,0))
        label = tk.Label(home_window, text="Do you have another question for the same paragraph?")
        label.pack()
        def clear_entries():
            question_entry.delete(0, tk.END)   # Clear question entry field   
            start_index.delete(0, tk.END) # Clear starting index entry field
            end_index.delete(0,tk. END)   # Clear ending index entry field
            content_label.tag_remove("sel", "1.0", "end")
        def next_paragraph():
            global paragraphs
            global current_paragraph_index
            
            # Increment the current paragraph index
            current_paragraph_index += 1
            
            # Check if there are more paragraphs to show
            if current_paragraph_index < len(paragraphs):
                # Show the next paragraph
                next_paragraph = paragraphs[current_paragraph_index]
                content_label.delete('1.0', tk.END) # clear existing content
                content_label.insert(tk.END, next_paragraph)
            else:
                # No more paragraphs to show
                tk.messagebox.showinfo("End of content", "No more paragraphs to show.")


        # create button for 'Yes'
        button_yes = tk.Button(home_window, text="Yes", command=lambda: clear_entries())
        button_yes.pack()

        # create button for 'No'
        button_no = tk.Button(home_window, text="No", command=lambda: next_paragraph())
        button_no.pack()
        # Check session expiration on a timer
        def check_session():
            cursor.execute("SELECT s.*, u.username FROM sessions s JOIN users u ON s.user_id = u.id WHERE s.id = %s AND s.last_activity >= DATE_SUB(NOW(), INTERVAL 30 MINUTE)", (session_id,))

            session = cursor.fetchone()
            if session:
                # Update session last_activity timestamp
                
                cursor.execute("UPDATE sessions SET last_activity=NOW() WHERE id=%s", (session_id,))
                db.commit()
                # Schedule next check
                home_window.after(60000, check_session) # Check again in 1 minute
            else:
                # Redirect to login page
                home_window.destroy() # Destroy current window
                root.deiconify() # Show login window
        home_window.after(60000, check_session) # Check session after 1 minute
    else:
        # Show error message
        error_label.config(text="Invalid username or password")

login_button = tk.Button(root, text="Login", command=login,bg="light pink")
login_button.pack()

# Create signup button
def signup():
    # Retrieve username and password inputs
    username = username_entry.get()
    password = password_entry.get()

    # Insert new user into database
    cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
    db.commit()

    # Show success message
    success_label.config(text="User created successfully")

signup_button = tk.Button(root, text="Signup", command=signup,bg="lightpink")
signup_button.pack()

# Create error and success message labels
error_label = tk.Label(root, fg="red")
error_label.pack()
success_label = tk.Label(root, fg="green")
success_label.pack()
root.mainloop()
