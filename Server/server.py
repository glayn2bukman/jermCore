from flask import Flask, request, Response, send_from_directory
import os, cPickle, time

app = Flask(__name__)

jermUSER = {"jerm":"jerm123#"}
jermExt = ".jerm"

path = os.path.dirname(__file__)
projects_dir = os.path.join(path, "projects")

ERRORS = {
    "auth-error":"ERROR: authentication Error!",
    "file-error":"ERROR: file not found in jermProjects!",
    "filename-error":"ERROR: file name contains invalid characters!",
    "nofile-error":"ERROR: no file given in attachments!",
    "notjermproject-error":"ERROR: file is NOT a jerm  project!",
    "version-error":"ERROR: version contains invalid characters (/, .. and \\ are not allowed)!",
    "noversion-error": "ERROR: no version was given for the project!",
    "noproject-error":"ERROR: no project given!",
    "noprojectversion-error":"ERROR: the project version specified does no exist!",
    "userexists-error":"ERROR: user exists in the system!",
    "usernotinsystem-error":"ERROR: user not in the system!",
    "oldcredentialsdontmatch-error":"ERROR: old credentials dont match existing records!",
    "sillyform-error":"ERROR: invalid form sent. is this dracula?"
}

##################################### LOGGING ###########################################
if not os.path.isfile(os.path.join(path, "log.jermlog")):
    with open(os.path.join(path, "log.jermlog"), "w+") as f: pass
def log(msg):
    print "**jermlog** ({}) {}".format(time.asctime(), msg.replace("\n", "."))
    with open(os.path.join(path, "log.jermlog"), "a+") as f: 
        f.write("\n({}) {}".format(time.asctime(), msg.replace("\n", ".")))
    

##################################### USER ACCOUNTS #####################################
def authenticate(uname, pswd):
    if not os.path.isfile(os.path.join(path, "jerm-dracula-users.jermauth")): 
        cPickle.dump(jermUSER, open(os.path.join(path, "jerm-dracula-users.jermauth"), "wb"), 2)
        return 0

    users = cPickle.load(open(os.path.join(path, "jerm-dracula-users.jermauth"), "rb"))

    if not (uname in users): return 0
    if  users[uname]!=pswd: return 0
    return 1

def add_user(uname, pswd):
    if not os.path.isfile(os.path.join(path, "jerm-dracula-users.jermauth")):
        cPickle.dump(jermUSER, open(os.path.join(path, "jerm-dracula-users.jermauth"), "wb"), 2)

    users = cPickle.load(open(os.path.join(path, "jerm-dracula-users.jermauth"), "rb"))

    if (uname in users): return ERRORS["userexists-error"]

    users[uname] = pswd
    cPickle.dump(users, open(os.path.join(path, "jerm-dracula-users.jermauth"), "wb"), 2)

    return "User added sucessfully!"

def get_all_users():
    if not os.path.isfile(os.path.join(path, "jerm-dracula-users.jermauth")):
        cPickle.dump(jermUSER, open(os.path.join(path, "jerm-dracula-users.jermauth"), "wb"), 2)

    users = cPickle.load(open(os.path.join(path, "jerm-dracula-users.jermauth"), "rb"))

    return users.keys()

def delete_user(uname):
    if not os.path.isfile(os.path.join(path, "jerm-dracula-users.jermauth")):
        cPickle.dump(jermUSER, open(os.path.join(path, "jerm-dracula-users.jermauth"), "wb"), 2)

    users = cPickle.load(open(os.path.join(path, "jerm-dracula-users.jermauth"), "rb"))

    if not(uname in users): return ERRORS["usernotinsystem-error"]

    del(users[uname])

    cPickle.dump(users, open(os.path.join(path, "jerm-dracula-users.jermauth"), "wb"), 2)

    return "User deleted from system sucessfully!"

def edit_account(uname, pswd, new_pswd):
    if not os.path.isfile(os.path.join(path, "jerm-dracula-users.jermauth")):
        cPickle.dump(jermUSER, open(os.path.join(path, "jerm-dracula-users.jermauth"), "wb"), 2)

    users = cPickle.load(open(os.path.join(path, "jerm-dracula-users.jermauth"), "rb"))

    if not(uname in users): return ERRORS["usernotinsystem-error"]
    
    if users[uname]!=pswd: return ERRORS["oldcredentialsdontmatch-error"]

    users[uname] = new_pswd

    cPickle.dump(users, open(os.path.join(path, "jerm-dracula-users.jermauth"), "wb"), 2)

    return "password changed sucessfully"
    
##################################### USER ACCOUNTS #####################################

# define a function that wil allow responses to be sent to pages not served by this server
def reply_to_remote(reply):
    response = Response(reply)
    response.headers["Access-Control-Allow-Origin"] = "*" # allow all domains...
    return response

@app.route("/data", methods=["POST"])
def jerm_dracula_data():
    if not (("master" in request.form) and ("data" in request.form)): return reply_to_remote(ERRORS["sillyform-error"])
    
    data = request.form["data"].split(";")
    
    if data[0]!="edit-user":
        # only the jerm super admin/user may do this...
        if jermUSER.keys()[0]+";"+jermUSER.values()[0] != request.form["master"]: return reply_to_remote(ERRORS["auth-error"])
    
    if data[0]=="add-user":
        status = add_user(data[1], data[2])
    elif data[0]=="edit-user":
        status = edit_account(data[1], data[2], data[3])
    elif data[0]=="delete-user":
        status = delete_user(data[1])
    elif data[0]=="all-users":
        status = get_all_users()

        _s = ""
        for i, s in enumerate(status): _s += "\n {}) {}".format(i+1, s)
        
        status = _s

    return reply_to_remote(status)        
   
@app.route("/upload_project", methods=["POST"])
def upload_project():
    if not(("uname" in request.form) and ("pswd" in request.form)): return reply_to_remote(ERRORS["auth-error"])

    if not authenticate(request.form["uname"], request.form["pswd"]): return reply_to_remote(ERRORS["auth-error"])
    log("user <{}> logged in".format(request.form["uname"]))

    if not request.files: return reply_to_remote(ERRORS["nofile-error"])
    if not ("project" in request.files): return reply_to_remote(ERRORS["nofile-error"])
    if not ("version" in request.form): return reply_to_remote(ERRORS["noversion-error"])

    project = request.files["project"]
    version = request.form["version"]
    
    if (".." in version) or ("/" in version) or ("\\" in version): return reply_to_remote(ERRORS["version-error"])

    if ("/" in project.filename) or ("\\" in project.filename): return reply_to_remote(ERRORS["filename-error"])
    if not (project.filename.endswith(jermExt)): return reply_to_remote(ERRORS["notjermproject-error"])

    projectname = ".".join(project.filename.split(".")[:-1])

    if not os.path.isdir(os.path.join(projects_dir, projectname)): os.mkdir(os.path.join(projects_dir, projectname))

    project.save(os.path.join(projects_dir, projectname, version+jermExt))
    
    log("project <{}>, version <{}> uploaded".format(project, version))
    
    return reply_to_remote("project uploaded sucesfully")

@app.route("/list_projects", methods=["POST"])
def list_projects():
    if not(("uname" in request.form) and ("pswd" in request.form)): return reply_to_remote(ERRORS["auth-error"])
    if not authenticate(request.form["uname"], request.form["pswd"]): return reply_to_remote(ERRORS["auth-error"])
    log("user <{}> logged in".format(request.form["uname"]))

    projects = os.listdir(projects_dir)

    log("user <{}> listing all jerm projects".format(request.form["uname"]))

    return reply_to_remote(",".join(projects))

@app.route("/list_project_versions", methods=["POST"])
def list_project_versions():
    if not(("uname" in request.form) and ("pswd" in request.form)): return reply_to_remote(ERRORS["auth-error"])
    if not ("project" in request.form): return reply_to_remote(ERRORS["noproject-error"])

    if not authenticate(request.form["uname"], request.form["pswd"]): return reply_to_remote(ERRORS["auth-error"])
    log("user <{}> logged in".format(request.form["uname"]))

    project = request.form["project"]

    if not os.path.isdir(os.path.join(projects_dir, project)): return reply_to_remote("project <{}>is unknown".format(project))

    versions = os.listdir(os.path.join(projects_dir, project))

    log("user <{}> listing all versions of project <{}>".format(request.form["uname"], project))

    return reply_to_remote("\n".join(versions))

@app.route("/fetch_project_version", methods=["POST"])
def fetch_project_version():
    if not(("uname" in request.form) and ("pswd" in request.form)): return reply_to_remote(ERRORS["auth-error"])

    if not authenticate(request.form["uname"], request.form["pswd"]): return reply_to_remote(ERRORS["auth-error"])
    log("user <{}> logged in".format(request.form["uname"]))

    if not ("project" in request.form): return reply_to_remote(ERRORS["noproject-error"])
    if not ("version" in request.form): return reply_to_remote(ERRORS["noversion-error"])
    
    project = request.form["project"]
    projectversion = request.form["version"]

    if not os.path.isfile(os.path.join(projects_dir, project, projectversion)): return reply_to_remote(ERRORS["noprojectversion-error"])

    log("user <{}> fetching project <{}>, version <{}>".format(request.form["uname"], project, projectversion))

    return send_from_directory(os.path.join(projects_dir, project), projectversion)

@app.route("/log-project-fetch", methods=["POST"])
def log_project_fetch():
    if not(("uname" in request.form) and ("project" in request.form) and ("version" in request.form)): return "ERROR: invalid form sent. is this dracula?"

    log("user <{}> fetching project <{}>, version <{}>".format(
        request.form["uname"],
        request.form["project"],
        request.form["version"],
    ))
    return reply_to_remote("0")

if __name__=="__main__":
    import threading
    threading.Thread(target=os.system, args=("twistd -n web --path=\"{}\" -p 9998".format(os.path.join(path, "projects")), )).start()
    app.run("0.0.0.0", 9997, debug=1, threaded=1)
    
    
