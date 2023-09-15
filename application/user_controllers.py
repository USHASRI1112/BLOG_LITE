import os
from flask import render_template, request, redirect, session, flash
from flask import current_app as app
from application.models import User, UserRelation, Blog
from application.database import db
from application.blog_controllers import allowed_file
from werkzeug.utils import secure_filename


@app.route("/", methods=["GET", "POST"])
def index():
    session["logged_user"] = None
    return render_template("index.html")


@app.route("/home", methods=["GET", "POST"])
def home():
    if session["logged_user"] is not None:
        # for current login user get list of following-id
        result = UserRelation.query.filter_by(
            follower_id=session.get("logged_user")["id"]
        ).all()
        followingidList = []
        for item in result:
            followingidList.append(item.following_id)
        blogList = Blog.query.filter(Blog.user_id.in_(followingidList)).all()
        print(result)
        print(followingidList)
        print(blogList)
        profiles = []
        for i in blogList:
            profile = (
                User.query.filter_by(id=i.user_id)
                .with_entities(User.profile_photo)
                .first()
            )
            profiles.append(profile[0])
        print(profiles)
        combined = zip(blogList, profiles)
        for i in combined:
            print(i)
        return render_template(
            "home.html",
            blogList=blogList,
            Username=session.get("logged_user")["username"],
            profiles=profiles,
        )
    else:
        redirect("/")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        user = User()
        user.username = request.form["username"]
        user.password = request.form["password"]
        confirm_password = request.form["confirm_password"]
        file = request.files["file"]
        if User.query.filter_by(username=user.username).count() > 0:
            flash("Signup Unsuccessful. Username already exist.", "danger")
            return render_template("signup.html")
        if confirm_password == user.password:
            user.no_of_followers = 0
            user.no_of_posts = 0
            user.profile_photo = file.filename
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            db.session.add(user)
            db.session.commit()
            return redirect("/")
        else:
            flash(
                "Password and ConfirmPassword aren't same",
                "danger",
            )
            return render_template("signup.html")
    else:
        return render_template("signup.html")


@app.route("/login", methods=["POST"])
def login():
    if session["logged_user"] is None:
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()
        if user is not None:
            if user.password == password:
                session["logged_user"] = {
                    "id": user.id,
                    "username": user.username,
                    "password": user.password,
                    "no_of_followers": user.no_of_followers,
                    "no_noteof_posts": user.no_of_posts,
                }
                return redirect("/home")
            else:
                return "Record not found", 400
        else:
            return "Record not found", 400
    else:
        return redirect("/home")


@app.route("/logout", methods=["GET", "POST"])
def logout():
    return redirect("/")


@app.route("/searchuser", methods=["POST"])
def searchuser():
    searchTxt = request.form["searchuser"]
    result = User.query.filter(User.username.contains(searchTxt)).all()
    return render_template(
        "searchuser.html",
        userlist=result,
        userid=session.get("logged_user")["id"],
        Username=session.get("logged_user")["username"],
    )


@app.route("/user/<int:id>/<string:username>", methods=["GET"])
def user(id, username):
    isFollow = True
    result = len(
        UserRelation.query.filter_by(
            follower_id=session.get("logged_user")["id"], following_id=id
        ).all()
    )
    if result == 0:
        isFollow = False
    return render_template(
        "followunfollow.html",
        followingid=id,
        username=username,
        isFollow=isFollow,
        Username=session.get("logged_user")["username"],
    )


@app.route("/unfollowuser/<int:followingid>/<string:username>", methods=["GET"])
def unfollowuser(followingid, username):
    UserRelation.query.filter_by(
        follower_id=session.get("logged_user")["id"],
        following_id=followingid,
        following_username=username,
    ).delete()
    User.query.filter_by(id=session.get("logged_user")["id"]).update(
        {"no_of_followers": User.no_of_followers - 1}
    )
    db.session.commit()
    return redirect("/home")


@app.route("/followuser/<int:followingid>/<string:username>", methods=["GET"])
def followuser(followingid, username):
    userRelation = UserRelation()
    userRelation.follower_id = session.get("logged_user")["id"]
    userRelation.following_id = followingid
    userRelation.follower_username = session.get("logged_user")["username"]
    userRelation.following_username = username
    db.session.add(userRelation)
    User.query.filter_by(id=session.get("logged_user")["id"]).update(
        {"no_of_followers": User.no_of_followers + 1}
    )
    db.session.commit()
    return redirect("/home")


@app.route("/myprofile", methods=["GET"])
def myprofile():
    followed = UserRelation.query.filter_by(
        follower_id=session.get("logged_user")["id"]
    ).count()
    followedby = UserRelation.query.filter_by(
        following_id=session.get("logged_user")["id"]
    ).count()
    bloglist = Blog.query.filter_by(user_id=session.get("logged_user")["id"]).all()
    user = User.query.get(session.get("logged_user")["id"])
    return render_template(
        "myprofile.html",
        Username=session.get("logged_user")["username"],
        followed=followed,
        followedby=followedby,
        bloglist=bloglist,
        user=user,
    )


@app.route("/listoffollowed", methods=["GET"])
def listoffollowed():
    followed = UserRelation.query.filter_by(
        follower_id=session.get("logged_user")["id"]
    ).all()
    return render_template(
        "listoffollowed.html",
        followed=followed,
        Username=session.get("logged_user")["username"],
    )


@app.route("/unfollowfollowed/<int:following_id>", methods=["GET"])
def unfollowfollowed(following_id):
    UserRelation.query.filter_by(
        follower_id=session.get("logged_user")["id"], following_id=following_id
    ).delete()
    User.query.filter_by(id=session.get("logged_user")["id"]).update(
        {"no_of_followers": User.no_of_followers - 1}
    )
    db.session.commit()
    return redirect("/listoffollowed")


@app.route("/listoffollowedby", methods=["GET"])
def listoffollowedby():
    followed = UserRelation.query.filter_by(
        follower_id=session.get("logged_user")["id"]
    ).all()
    maplist = {}
    for item in followed:
        maplist[item.following_id] = item.follower_id
    print(maplist)
    followedby = UserRelation.query.filter_by(
        following_id=session.get("logged_user")["id"]
    ).all()
    return render_template(
        "listoffollowedby.html",
        followedby=followedby,
        Username=session.get("logged_user")["username"],
        Userid=session.get("logged_user")["id"],
        maplist=maplist,
    )


@app.route(
    "/followfollowedby/<int:follower_id>/<string:follower_username>", methods=["GET"]
)
def followfollowedby(follower_id, follower_username):
    userRelation = UserRelation()
    userRelation.follower_id = session.get("logged_user")["id"]
    userRelation.following_id = follower_id
    userRelation.follower_username = session.get("logged_user")["username"]
    userRelation.following_username = follower_username
    db.session.add(userRelation)
    User.query.filter_by(id=session.get("logged_user")["id"]).update(
        {"no_of_followers": User.no_of_followers + 1}
    )
    db.session.commit()
    return redirect("/listoffollowedby")


@app.route("/unfollowfollowedby/<int:follower_id>", methods=["GET"])
def unfollowfollowedby(follower_id):
    UserRelation.query.filter_by(
        follower_id=follower_id, following_id=session.get("logged_user")["id"]
    ).delete()
    User.query.filter_by(id=follower_id).update(
        {"no_of_followers": User.no_of_followers - 1}
    )
    db.session.commit()
    return redirect("/listoffollowedby")
