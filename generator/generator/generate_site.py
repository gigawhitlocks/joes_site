from boto.s3.connection import S3Connection
import boto.s3.connection
import os
import argparse
from generator import render_template

def main():

    parser = argparse.ArgumentParser(description='Joe\'s Custom Site Generator!')
    parser.add_argument('--upload', help='Add --upload after the command to upload the site to s3!', dest='upload',
                        default=False, action='store_true')
    parser.add_argument('project_dir',
                        help='The full path to the location of the project root, where sitemap.yml can be found')

    args = parser.parse_args()

    os.chdir(args.project_dir)
    cwd = os.getcwd()
    if not 'sitemap.yml' in os.listdir('.'):
        raise Exception('SANITY CHECK! Aborting due to execution in unknown directory!')

    print "Setting up system.."
    os.system("rm -rf output/")
    os.system("mkdir -p output/work")
    os.system("ln -s {}/output/work.html {}/output/index.html".format(cwd, cwd))
    render_template.set_testroot(args.project_dir)

    print("Rendering templates..")
    for template in os.listdir('templates'):
        if not render_template.get_sitemap().get(template.split(".")[0], False):
            continue
        render_template.render_template(template, args.upload, args.project_dir)

    for asset in os.listdir('assets'):
        os.system("ln -s {}/assets/{} {}/output/{}".format(cwd, asset, cwd, asset))

    if args.upload:
        conn = S3Connection(os.getenv('JOE_AWS'), os.getenv('JOE_AWS_SECRET'),
                            calling_format=boto.s3.connection.OrdinaryCallingFormat())
        bucket = conn.get_bucket('josephhader.com')
        print("Uploading assets..")
        render_template.upload_assets(bucket)

    os.chdir('output')
    print("Starting preview server..")
    import SimpleHTTPServer
    import SocketServer
    PORT = 8000

    def start_server():
        import socket
        try:
            SimpleHTTPHandler = SimpleHTTPServer.SimpleHTTPRequestHandler
            httpd = SocketServer.TCPServer(("", PORT), SimpleHTTPHandler)
            return httpd
        except socket.error:
            return False

    import time
    started = False
    httpd = None
    while not started:
        started = start_server()
        if not started:
            for i in range(30,0,-1):
                print "Socket in use; sleeping {} seconds".format(i)
                time.sleep(1)
        else:
            httpd = started

    print "Navigate to http://localhost:{} in your browser to see a preview of the site".format(PORT)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.shutdown()
        print "Thank you for flying Whitlock Airlines"


if __name__ == "__main__":
    main()
