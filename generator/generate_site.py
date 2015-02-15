"""
"""
from boto.s3.connection import S3Connection
from boto.s3.key import Key

from jinja2 import Environment, PackageLoader
import markdown
import argparse
import os

env = Environment(loader=PackageLoader('generate_site', '../templates'))
PRODROOT = '/home/zuul/joe/'

JINJA_CONSTANTS = {
    'SITE_URL': 'http://josephhader.com',
    'NAV_ELEMENTS': ['about', 'design', 'video', 'resume', 'contact']
}

def get_post(post_name):
    try:
        return markdown.markdown(
            markdown.codecs.open(PRODROOT+"content/"+post_name+".md",
                                 mode="r",
                                 encoding="utf-8").read())
    except IOError:
        return "No post content found"


def render_template(template, **kwargs):
    """foo
    """
    template = env.get_template(template)
    return template.render(**kwargs)

def upload_assets(bucket):
    assets = [ asset.split('assets/')[1]
               for asset in [os.path.join(dp, f)
                             for dp, _, fn in os.walk(
                                     os.path.expanduser(
                                         PRODROOT+"assets/"))
                             for f in fn]]
    for asset in assets:
        if asset.startswith('~') or asset.startswith('#'):
            continue
        key = bucket.new_key(asset)
        key.set_contents_from_file(open(PRODROOT+"assets/"+asset, 'rb'), policy='public-read')

def upload_site(template_name, rendered_template):
    conn = S3Connection(os.getenv('JOE_AWS'), os.getenv('JOE_AWS_SECRET'))
    bucket = conn.get_bucket('josephhader.com')
    upload_assets(bucket)

    bucket_template = bucket.new_key(template_name)
    bucket_template.set_metadata('content-type', 'text/html')
    bucket_template.set_contents_from_string(
        rendered_template, policy='public-read')

def main():
    """pylint
    """

    parser = argparse.ArgumentParser(description='Process a template')
    parser.add_argument('template',
                        help='The name of the template, including .html')
    parser.add_argument('--upload', help='upload to s3?', dest='upload',
                        default=False, action='store_true')
    args = parser.parse_args()
    rendered_page = str(render_template(args.template,
                                        post_content=get_post(
                                            args.template.split(".")[0]),
                                        **JINJA_CONSTANTS))
    if args.upload:
        upload_site(args.template, rendered_page)
    else:
        print(rendered_page)


if __name__ == "__main__":
    main()
