from functools import reduce

from flask import Flask, request, render_template, send_from_directory, redirect
import json

POST_PATH = "posts.json"
UPLOAD_FOLDER = "uploads/images"

app = Flask(__name__)


def load_posts(file_name):
    with open(file_name, encoding='utf-8') as f:
        return json.load(f)


def save_posts(posts, file_name):
    with open(file_name, 'w', encoding='utf-8') as f:
        return json.dump(posts, f)


def get_tags_from_text(text):
    return list(set([tag for tag in text.split(' ') if tag.startswith('#')]))


def get_tags_from_posts(posts):
    return set(reduce(lambda acc, i: acc + get_tags_from_text(i['content']), posts, []))


def filter_posts(posts, tag_name):
    filtered_posts = []

    for post in posts:
        tags = get_tags_from_text(post['content'])

        if tag_name in tags:
            filtered_posts.append(post)

    return filtered_posts


def append_post(content, file):
    url = f'./uploads/images/{file.filename}'

    file.save(url)

    post = {'pic': url, 'content': content}
    post_list.append(post)

    save_posts(post_list, POST_PATH)

    return post


post_list = load_posts(POST_PATH)
tag_list = get_tags_from_posts(post_list)


@app.route("/")
def page_index():
    return render_template('index.html', tags=tag_list)


@app.route("/tag")
def page_tag():
    tag_name = request.args.get('tag')
    posts = filter_posts(post_list, tag_name)
    return render_template('post_by_tag.html', posts=posts, tag_name=tag_name)


@app.route("/post", methods=["GET"])
def page_post_view():
    return render_template('post_form.html')


@app.route("/post", methods=["POST"])
def page_post_create():
    post_content = request.form.get('content')
    post_file = request.files.get('picture')

    if not post_file or not post_content:
        return redirect('/post')

    post = append_post(post_content, post_file)

    return render_template('post_uploaded.html', post=post)


@app.route("/uploads/<path:path>")
def static_dir(path):
    return send_from_directory("uploads", path)


app.run(debug=True)

