from frontend import app
from flask import request, redirect, \
                  render_template, flash, make_response
import json, requests
from views import check


headers={'Content-Type': 'application/json'}

app.config['PROPAGATE_EXCEPTIONS'] = True


@app.route('/posts', methods=['POST', 'GET'])
def posts():
    res = check()
    if res.status_code == 200 and request.method == 'GET':
        status = {'user_status_code': True, 'post_status_code': False, 'permission_add_post_code': True}
        res = json.loads(res.text)
        userid = res['userid']
        if 'userid' in request.args:
            status['permission_add_post_code'] = False
            userid = request.args['userid']

        res_b1 = requests.get('http://localhost:8001/me/'+str(userid), headers=headers)
        
        if res_b1.status_code != 200:
            status['user_status_code'] = False
            return render_template('layout.html', access=True, status=status)
        user = json.loads(res_b1.text)

        page = 1
        if 'page' in request.args:
            page = request.args.get('page')

        body = json.dumps({'page': page, 'userid': userid})
        res_b2 = requests.get('http://localhost:8002/posts', data=body, headers=headers)
        status['post_status_code'] = False
        if res_b2.status_code == 200:
            res = json.loads(res_b2.text)
            status['post_status_code'] = True
        return render_template('posts.html', access=True, posts=res, user=user, status=status)

    return redirect('index')


@app.route('/comments/add', methods=['GET', 'POST'])
def addcomments():
    res = check()
    if res.status_code == 200 and request.method == 'POST':
        res = json.loads(res.text)
        res_b1 = requests.get('http://localhost:8001/me/'+str(res['userid']), headers=headers)
        status = {'user_status_code': True, 'post_status_code': False}
        if res_b1.status_code != 200:
            status['user_status_code'] = False
            return render_template('layout.html', access=True, status=status)
        user = json.loads(res_b1.text)



    return redirect('index')


@app.route('/posts/add', methods=['POST'])
def addposts():
    if request.method == 'POST':
        key = request.cookies.get('key')
        if key is not None:
            body = json.dumps({'key': key})
            res = requests.post('http://localhost:8003/status', data=body, headers=headers)
            if res.status_code == 200:
                title = request.form['title']
                text = request.form['text']
                data = {'entry': {'userid': json.loads(res.text)['userid'], 'title': title, 'text': text}}
                body = json.dumps(data)
                res_b2 = requests.post('http://localhost:8002/posts/add', data=body, headers=headers)
                if res_b2.status_code == 200:
                    flash('New entry was successfully posted')
                else:
                    flash('failed add new entry')

                return redirect('/posts')
            else:
                flash(json.loads(res.text)['error'])
                return redirect('/posts')
        else:
            return redirect('/logout')

    return render_template('posts.html')


@app.route('/posts/allusers')
def all():
    key = request.cookies.get('key')
    if key is not None:
        body = json.dumps({'key': key})
        res = requests.post('http://localhost:8003/status', data=body, headers=headers)
        if res.status_code == 200:
            userid = json.loads(res.text)
            body = json.dumps(userid)
            res_b1 = requests.get('http://localhost:8001/me', data=body, headers=headers)
            if res_b1.status_code == 200:
                datame = json.loads(res_b1.text)

            res_b2 = requests.get('http://localhost:8002/posts', headers=headers)
            if res_b2.status_code == 200:
                dataentry = json.loads(res_b2.text)

            r = []
            for usr in datame:
                entr = []
                for e in dataentry:
                    if usr['userid'] == e['userid']:
                        entr.append({'title': e['title'], 'text': e['text']})

                r.append({'username': usr['username'], 'entry': entr})

            res_b1 = requests.get('http://localhost:8001/me/'+str(userid['userid']), headers=headers)
            user = json.loads(res_b1.text)
            return render_template('index.html', posts=r, user=user, access=True)
    else:
        return redirect('/logout')

    return redirect('/posts')
