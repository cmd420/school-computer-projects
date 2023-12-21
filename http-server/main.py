import json
import random
import string
from pathlib import Path
from datetime import datetime
from simple_http_server import HTTPServer, HTTPRequest, HTTPResponseBuilder
import urllib.parse

server = HTTPServer('127.0.0.1', 8080)
blogs  = []


def random_str(length: int = 6) -> str:
    ret = ''
    chars = string.ascii_lowercase + string.digits

    for _ in range(length):
        ret += random.choice(chars)

    return ret


@server.route('/', methods=['GET', 'POST'])
def index(request: HTTPRequest):
    if request.method == 'POST':
        now = datetime.now()
        date = now.strftime('%d/%m/%Y, %I:%M %p')

        title = urllib.parse.unquote_plus(request.form.get('title', 'Blog Title'))
        content = urllib.parse.unquote_plus(request.form.get('content', ''))
        blog_id = random_str()
        url = '/blogs?id=' + blog_id

        blog = {
            'title': title,
            'url': url,
            'date': date
        }

        with open('./templates/blog_template.html', 'r') as template_file,\
            open(f'./templates/blog-{blog_id}.html', 'w+') as file:
            template = template_file.read()
            template = template.replace('{{title}}', title)
            template = template.replace('{{content}}', content)
            template = template.replace('{{date}}', date)

            file.write(template)

        blogs.append(blog)
        with open('blogs.json', 'w+') as file:
            file.write(json.dumps(blogs))

    return HTTPResponseBuilder().from_template('./templates/index.html')

@server.route('/blogs')
def list_blogs(request: HTTPRequest):
    blog_id = request.params.get('id')
    if not blog_id:
        return {'blogs': blogs}
    
    path = Path('./templates')
    path /= f'blog-{blog_id}.html'
    if not path.exists():
        return (404, 'Blog Not Found')
    
    return HTTPResponseBuilder().from_template(str(path))

if __name__ == '__main__':
    with open('blogs.json', 'r') as file:
        blogs = json.load(file)

    server.run()