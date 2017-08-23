from flask import Flask, request, Response, send_from_directory
import os

app = Flask(__name__)

auth = {"uname":"jerm", "pswd":"jerm123#"}
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
}

# define a function that wil allow responses to be sent to pages not served by this server
def reply_to_remote(reply):
    response = Response(reply)
    response.headers["Access-Control-Allow-Origin"] = "*" # allow all domains...
    return response


@app.route("/upload_project", methods=["POST"])
def upload_project():
    if not(("uname" in request.form) and ("pswd" in request.form)): return reply_to_remote(ERRORS["auth-error"])
    if request.form["uname"]!=auth["uname"] or request.form["pswd"]!=auth["pswd"]: return reply_to_remote(ERRORS["auth-error"])
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
    
    return reply_to_remote("project uploaded sucesfully")

@app.route("/list_projects", methods=["POST"])
def list_projects():
    if not(("uname" in request.form) and ("pswd" in request.form)): return reply_to_remote(ERRORS["auth-error"])
    if request.form["uname"]!=auth["uname"] or request.form["pswd"]!=auth["pswd"]: return reply_to_remote(ERRORS["auth-error"])

    projects = os.listdir(projects_dir)

    return reply_to_remote(",".join(projects))

@app.route("/list_project_versions", methods=["POST"])
def list_project_versions():
    if not(("uname" in request.form) and ("pswd" in request.form)): return reply_to_remote(ERRORS["auth-error"])
    if not ("project" in request.form): return reply_to_remote(ERRORS["noproject-error"])

    if request.form["uname"]!=auth["uname"] or request.form["pswd"]!=auth["pswd"]: return reply_to_remote(ERRORS["auth-error"])

    project = request.form["project"]

    if not os.path.isdir(os.path.join(projects_dir, project)): return reply_to_remote("project <{}>is unknown".format(project))

    versions = os.listdir(os.path.join(projects_dir, project))

    return reply_to_remote("\n".join(versions))

@app.route("/fetch_project_version", methods=["POST"])
def fetch_project_version():
    if not(("uname" in request.form) and ("pswd" in request.form)): return reply_to_remote(ERRORS["auth-error"])
    if request.form["uname"]!=auth["uname"] or request.form["pswd"]!=auth["pswd"]: return reply_to_remote(ERRORS["auth-error"])
    if not ("project" in request.form): return reply_to_remote(ERRORS["noproject-error"])
    if not ("version" in request.form): return reply_to_remote(ERRORS["noversion-error"])
    
    project = request.form["project"]
    projectversion = request.form["version"]

    if not os.path.isfile(os.path.join(projects_dir, project, projectversion)): reply_to_remote(ERRORS["noprojectversion-error"])

    return send_from_directory(os.path.join(projects_dir, project), projectversion)

print path
if __name__=="__main__":
    import threading
    threading.Thread(target=os.system, args=("twistd -n web --path=\"{}\" -p 9998".format(os.path.join(path, "projects")), )).start()
    app.run("0.0.0.0", 9999, debug=1, threaded=1)
    
    
