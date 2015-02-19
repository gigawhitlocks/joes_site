"""
"""
from boto.s3.connection import S3Connection

from jinja2 import Environment, PackageLoader
import pyembed.core.parse
pyembed.core.parse.PARSE_FUNCTIONS['application/xml'] = pyembed.core.parse.parse_oembed_xml

import markdown
from pyembed.markdown import PyEmbedMarkdown
import argparse
import os
import yaml

TESTROOT = None
extra_templates = {}

JINJA_CONSTANTS = {
    'SITE_URL': None,
    'NAV_ELEMENTS': ['about', 'work', 'contact']
}
def get_post(post_name):
    try:
        output = markdown.markdown(
            markdown.codecs.open(TESTROOT+"content/"+post_name+".md",
                                 mode="r",
                                 encoding="utf-8").read(),
            extensions=[PyEmbedMarkdown()])
        return output
    except IOError:
        return False


def _translate_posts(pagemap):
    try:
        if pagemap.endswith(".md"):
            print "return get_post line 37 pagemap {}".format(pagemap)
            return get_post(pagemap.split(".md")[0])
        else:
            print "return pagemap line 39 {}".format(pagemap)
            return pagemap

    except AttributeError:
        try:
            if pagemap.get('expanded', None):
                filename = pagemap.get('expanded').split(".md")[0]
                with open(TESTROOT+
                          "output/"+filename+'.html', 'w') as outfile:
                    rendered_page = get_post(filename).encode('utf-8')
                    outfile.write(rendered_page)
                    global extra_templates
                    extra_templates['{}.html'.format(filename)] = rendered_page
                print "return pagemap line 53 {}".format(pagemap)
                return pagemap
            return { element: _translate_posts(pagemap[element]) for element in pagemap }
        except AttributeError:
            try:
                return { element: _translate_posts(pagemap[element]) for element in pagemap }
            except TypeError:
                return [ _translate_posts(element) for element in pagemap ]

def get_posts(page):
    sitemap = yaml.load_all(open(TESTROOT+"sitemap.yml")).next()
    new_sitemap = _translate_posts(sitemap[page])
    import pprint; pprint.pprint(new_sitemap)
    return _translate_posts(sitemap[page])

def _render_template(template, **kwargs):
    """foo
    """
    env = Environment(loader=PackageLoader('generator.render_template',
                                           "templates"))
    template = env.get_template(template)
    return template.render(**kwargs)

def upload_assets(bucket):
    assets = [ asset.split('assets/')[1]
               for asset in [os.path.join(dp, f)
                             for dp, _, fn in os.walk(
                                     os.path.expanduser(
                                         TESTROOT+"assets/"))
                             for f in fn]]
    for asset in assets:
        if asset.startswith('~') or asset.startswith('#'):
            continue
        key = bucket.new_key(asset)
        key.set_contents_from_file(open(TESTROOT+"assets/"+asset, 'rb'),
                                   policy='public-read')

def upload_template(bucket, template_name, rendered_template):
    bucket_template = bucket.new_key(template_name)
    bucket_template.set_metadata('content-type', 'text/html')
    bucket_template.set_contents_from_string(
        rendered_template, policy='public-read')

def render_template(template_name, upload_bool, testroot):
    """pylint
    """
    global TESTROOT
    TESTROOT = testroot + "/"
    print("Rendering {}".format(template_name))
    JINJA_CONSTANTS['TEMPLATE_URL'] = template_name
    JINJA_CONSTANTS['SITE_URL'] = 'http://josephhader.com' if upload_bool\
                                  else 'http://zuul.io:8000'
    if template_name != "base.html":
        post_content = get_posts(template_name.split(".")[0])
    else:
        post_content = None

    rendered_page = unicode(_render_template(template_name,
                                            post_content=post_content,
                                            **JINJA_CONSTANTS))
    if upload_bool:
        conn = S3Connection(os.getenv('JOE_AWS'), os.getenv('JOE_AWS_SECRET'))
        bucket = conn.get_bucket('josephhader.com')
        upload_template(bucket, template_name, rendered_page)

        for template in extra_templates:
            upload_template(bucket, template, extra_templates[template])

    with open(TESTROOT+"output/"+template_name, 'w') as output_file:
        output_file.write(rendered_page.encode('utf-8'))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process a template')
    parser.add_argument('template',
                        help='The name of the template, including .html')
    parser.add_argument('--upload', help='upload to s3?', dest='upload',
                        default=False, action='store_true')
    args = parser.parse_args()

    render_template(args.template, args.upload, '../../')
