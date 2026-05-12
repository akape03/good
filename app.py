from flask import Flask, flash, redirect, render_template, request, session, url_for
import os
from db import (init_db, check_account, add_account, get_all_posts, 
                create_post, get_post_by_post_id, update_post, delete_post, add_comment, get_comments)



app = Flask(__name__)
app.secret_key = os.urandom(32)


@app.route("/", methods=['GET'])
def get_index():
    if 'username' not in session:
        return redirect(url_for('get_login'))

    return render_template('index.html', username=session['username'])


@app.route('/posts', methods=['GET'])
def get_posts():
    if 'username' not in session:
        return redirect(url_for('get_login'))

    posts = get_all_posts()
    return render_template('posts.html', posts=posts)


@app.route('/posts/new', methods=['GET'])
def get_posts_new():
    if 'username' not in session:
        return redirect(url_for('get_login'))

    return render_template('posts_new.html')


@app.route('/posts/new', methods=['POST'])
def post_posts_new():
    if 'username' not in session:
        return redirect(url_for('get_login'))

    title = request.form.get('title')
    content = request.form.get('content')
    author_id = session['user_id']
    create_post(title, content, author_id)
    return redirect(url_for('get_posts'))


@app.route('/posts/<post_id>', methods=['GET'])
def get_posts_post_id(post_id):
    if 'username' not in session:
        return redirect(url_for('get_login'))

    post = get_post_by_post_id(post_id)
    if post:
        comments = get_comments(post_id) 
        return render_template('post.html', post=post, comments=comments)
    else:
        return redirect(url_for('get_posts'))


@app.route('/posts/<post_id>/comment', methods=['POST'])
def post_comment(post_id):
    if 'username' not in session:
        return redirect(url_for('get_login'))

    content = request.form.get('content')
    author_id = session.get('user_id') 
    
    if content and author_id:
        add_comment(post_id, author_id, content)
    
    return redirect(url_for('get_posts_post_id', post_id=post_id))


@app.route('/posts/<post_id>/edit', methods=['GET'])
def get_posts_post_id_edit(post_id):
    if 'username' not in session:
        return redirect(url_for('get_login'))

    post = get_post_by_post_id(post_id)
    if not post:
        return redirect(url_for('get_posts'))

    if post[3] != session['username']:
        flash("수정 권한이 없습니다.")
        return redirect(url_for('get_posts'))

    return render_template('post_edit.html', post=post)


@app.route('/posts/<post_id>/edit', methods=['POST'])
def post_posts_post_id_edit(post_id):
    if 'username' not in session:
        return redirect(url_for('get_login'))

    post = get_post_by_post_id(post_id)
    if not post:
        return redirect(url_for('get_posts'))

    if post[3] != session['username']:
        return render_template('post_edit_failure.html')

    title = request.form.get('title')
    content = request.form.get('content')
    update_post(post_id, title, content)
    return redirect(url_for('get_posts_post_id', post_id=post_id))


@app.route('/posts/<post_id>/delete', methods=['GET'])
def get_posts_post_id_delete(post_id):
    if 'username' not in session:
        return redirect(url_for('get_login'))

    post = get_post_by_post_id(post_id)
    if not post:
        return redirect(url_for('get_posts'))

    if post[3] != session['username']:
        flash("삭제 권한이 없습니다.")
        return redirect(url_for('get_posts'))

    return render_template('post_delete.html', post=post)


@app.route('/posts/<post_id>/delete', methods=['POST'])
def post_posts_post_id_delete(post_id):
    if 'username' not in session:
        return redirect(url_for('get_login'))

    post = get_post_by_post_id(post_id)
    if not post:
        return redirect(url_for('get_posts'))

    if post[3] != session['username']:
        return render_template('post_delete_failure.html')

    delete_post(post_id)
    return redirect(url_for('get_posts'))


@app.route("/register", methods=['GET'])
def get_register():
    if 'username' in session:
        return redirect(url_for('get_index'))

    return render_template('register.html')


@app.route("/register", methods=['POST'])
def post_register():
    if 'username' in session:
        return redirect(url_for('get_index'))

    username = request.form.get('username')
    password = request.form.get('password')
    if add_account(username, password):
        flash("회원가입 성공! 로그인해주세요.")
        return redirect(url_for('get_login'))
    else:
        flash("이미 존재하는 아이디거나 가입에 실패했습니다.")
        return redirect(url_for('get_register'))


@app.route("/login", methods=['GET'])
def get_login():
    if 'username' in session:
        return redirect(url_for('get_index'))

    return render_template('login.html')


@app.route("/login", methods=['POST'])
def post_login():
    if 'username' in session:
        return redirect(url_for('get_index'))

    username = request.form.get('username')
    password = request.form.get('password')
    user = check_account(username, password)
    if user:
        session['user_id'] = user[0]
        session['username'] = user[1]
        return redirect(url_for('get_index'))
    else:
        flash("아이디 또는 비밀번호가 틀렸습니다.")
        return redirect(url_for('get_login'))


@app.route("/logout", methods=['GET'])
def get_logout():
    session.clear()
    return redirect(url_for('get_login'))


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=31337)