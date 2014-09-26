import requests
import argparse
import json
from pprint import pprint

def main():
    parser = argparse.ArgumentParser(description='Consume a Swagger-UI site and'+
        'produce JSON that can be imported into API testing tools.')
    parser.add_argument('url', metavar='url', type=str, nargs='+',
                   help='root of the Swagger json docs')
    args = parser.parse_args()

    r = requests.get(args.url[0])
    if r.status_code == 200 and json.loads(r.content):
        api_root = json.loads(r.content)

        print("Located API. There are {} primary resources. Crawling each...".format(len(api_root["apis"])))

        for resource in api_root["apis"]:
            print("Adding endpoints for {} resource.".format(resource['path'][1:]))
            r = requests.get(args.url[0]+resource['path'])
            if r.status_code == 200 and json.loads(r.content):
                api_resource = json.loads(r.content)
                print api_resource
            else:
                raise Exception("No resource at specified URL")

    else:
        raise Exception("No resource at specified URL")




if __name__ == "__main__":
    main()