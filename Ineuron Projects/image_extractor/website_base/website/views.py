from uuid import uuid4

from flask import Blueprint, render_template, request, flash
from flask_login import login_required, current_user
from website.helper.image_downloader import download_images
import os
from website.models import User,sharedUsers

views = Blueprint('views', __name__)


@views.route('/', methods=['GET','POST'])
@login_required
def home():
    if request.method=='POST':

        topic = request.form.get('topic')
        n_images = int(request.form.get('n_images'))
        user_dir = current_user.first_name+"-"+current_user.last_name+"("+current_user.email_id+")"
        download_images(topic, n_images, user_dir)

    return render_template("home.html", user=current_user)


@views.route('/gallery', methods = ['GET','POST'])
@login_required
def gallery():

    folder_structure = None
    user_array = None

    try:
        folder_structure = {user_dir: {
                    user_sub_dir: ["/static/image-extractor/" + user_dir + "/" + user_sub_dir + "/" + files for files in
                                   os.listdir("./website/static/image-extractor/" + user_dir + "/" + user_sub_dir)] for user_sub_dir
                    in os.listdir("./website/static/image-extractor/" + user_dir)} for user_dir in
                              os.listdir("./website/static/image-extractor")}
    except:
        flash("no folders found!", category="error")

    if folder_structure:

        current_user_id = current_user.first_name + "-" + current_user.last_name + "(" + current_user.email_id + ")"
        current_shared_details = sharedUsers.objects(folder_id=current_user_id).first()
        shared_users = [current_user_id]
        if current_shared_details:
            shared_users = current_shared_details.shared_folder_id.split(",")
            shared_users.append(current_user_id)

        filtered_dictionary = {key: value for key, value in folder_structure.items() if key in shared_users}
        user_array = list(filtered_dictionary)
        if request.method == 'POST':
            user_id = request.form.get("user_folder")
            folder_id = request.form.get("folder_name")
            if user_id and folder_id is None:
                try:
                    user_folder = {user_id: list(filtered_dictionary[user_id])}
                    return render_template("gallery.html", user=current_user, user_dict=user_array, folder_dict=user_folder, render_dict=None)
                except:
                    flash(user_id+" not found!", category="error")
                    user_folder = {user_id: list(filtered_dictionary[current_user_id])}
                    return render_template("gallery.html", user=current_user, user_dict=user_array, folder_dict = user_folder, render_dict= None)

            if folder_id:

                folder_id = request.form.get("folder_name").replace("'", "").replace(" ","")
                user_id, folder_id = folder_id.split(",")[0][1:], folder_id.split(",")[1].replace(")","")
                files=folder_structure[user_id][folder_id]
                if user_id in user_array:
                    user_folder = {user_id: folder_structure[user_id].keys()}
                else:
                    flash(user_id + " not found!", category="error")
                    user_folder = {user_id: folder_structure[current_user_id].keys()}

                return render_template("gallery.html", user=current_user, user_dict=user_array, folder_dict=user_folder, render_dict=files)

    return render_template("gallery.html", user=current_user, user_dict=user_array, folder_dict=None, render_dict=None)

@views.route('/share', methods=['GET','POST'])
@login_required
def share():
    user_obj = User.objects()

    folder_id = [i.first_name+"-"+i.last_name+"("+i.email_id+")" for i in user_obj]

    user_folder_id = current_user.first_name+"-"+current_user.last_name+"("+current_user.email_id+")"

    shared_folder = []
    all_shared_users = sharedUsers.objects()
    for i in all_shared_users:
        if i.folder_id == user_folder_id:
            folder_id.remove(i.folder_id)
        else:
            if i.shared_folder_id:
                if user_folder_id in i.shared_folder_id.split(","):
                    folder_id.remove(i.folder_id)
                    shared_folder.append(i.folder_id)
    if user_folder_id in folder_id:
        folder_id.remove(user_folder_id)
    if request.method == 'POST':
        share_id = request.form.get('share_user')
        unshare_id = request.form.get('unshare_user')

        if share_id:
            add_user = sharedUsers.objects(folder_id=share_id).first()

            if add_user:

                folder_check = add_user.shared_folder_id
                if len(folder_check) == 0:
                    add_user.update(shared_folder_id=user_folder_id)
                    shared_folder.append(share_id)
                    folder_id.remove(share_id)
                else:
                    update_share_user = add_user.shared_folder_id.split(",")
                    update_share_user.append(user_folder_id)
                    share_user_to_string =','.join(update_share_user)
                    add_user.update(shared_folder_id=share_user_to_string)
                    shared_folder.append(share_id)
                    folder_id.remove(share_id)
            else:
                new_rec = sharedUsers.create(id=uuid4(),folder_id = share_id, shared_folder_id=user_folder_id)
                new_rec.save()
                shared_folder.append(share_id)
                folder_id.remove(share_id)
            return render_template("share.html", user=current_user, unshared_ids=folder_id, shared_users=shared_folder)

        if unshare_id:
            remove_user = sharedUsers.objects(folder_id=unshare_id).first()
            updated_share_user = remove_user.shared_folder_id.split(",").remove(user_folder_id)
            if updated_share_user:
                share_user_to_string = ','.join(updated_share_user)
                remove_user.update(shared_folder_id = share_user_to_string)
            else:
                remove_user.update(shared_folder_id="")
            shared_folder.remove(unshare_id)
            folder_id.append(unshare_id)

    return render_template("share.html", user=current_user, unshared_ids = folder_id, shared_users=shared_folder)