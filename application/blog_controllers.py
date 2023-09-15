import os
from flask import render_template, request,redirect,session
from flask import current_app as app
from application.models import Blog,User
from application.database import db
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/addpost", methods=["GET", "POST"])
def addpost():  
    if request.method == "POST":
        blog = Blog()
        blog.title = request.form['title']
        blog.caption_description = request.form['caption_description']
        file = request.files['file'] 
        blog.image_url=file.filename
        blog.user_id = session.get("logged_user")["id"]
        blog.user_name = session.get("logged_user")["username"]
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        db.session.add(blog)
        User.query.filter_by(id=session.get("logged_user")["id"]).update({'no_of_posts':User.no_of_posts+1})
        db.session.commit()
        return redirect('/home')
    else:
        return render_template("addPost.html")