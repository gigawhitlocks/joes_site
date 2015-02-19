from boto.s3.connection import S3Connection
import os
import argparse
from generator import render_template

def main():

    parser = argparse.ArgumentParser(description='Joe\' Custom Site Generator!')
    parser.add_argument('--upload', help='Add --upload after the command to upload the site to s3!', dest='upload',
                        default=False, action='store_true')
    parser.add_argument('project_dir',
                        help='The full path to the location of the project root, where sitemap.yml can be found')

    args = parser.parse_args()

    os.chdir(args.project_dir)
    cwd = os.getcwd()
    if not 'sitemap.yml' in os.listdir('.'):
        raise Exception('SANITY CHECK! Aborting due to execution in unknown directory!')

    os.system("rm -rf output/")
    os.system("mkdir -p output/work")
    os.system("ln -s {}/ouput/work.html {}/output/index.html".format(cwd, cwd))
    for template in os.listdir('templates'):
        render_template.render_template(template, args.upload, args.project_dir)

    for asset in os.listdir('assets'):
        os.system("ln -s {}/assets/{} {}/output/{}".format(cwd, asset, cwd, asset))

    if args.upload:
        conn = S3Connection(os.getenv('JOE_AWS'), os.getenv('JOE_AWS_SECRET'))
        bucket = conn.get_bucket('josephhader.com')
        print("Uploading assets..")
        render_template.upload_assets(bucket)

    os.chdir('output')
    print("Starting preview server..")
    import SimpleHTTPServer
    import SocketServer
    PORT = 8000
    SimpleHTTPHandler = SimpleHTTPServer.SimpleHTTPRequestHandler
    httpd = SocketServer.TCPServer(("", PORT), SimpleHTTPHandler)

    print "Serving at http://localhost:{}".format(PORT)
    httpd.serve_forever()


if __name__ == "__main__":
    main()