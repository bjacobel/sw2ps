import requests
import argparse
import json
from uuid import uuid4
from pprint import pprint
from datetime import datetime

class PSRequest:
    def __init__(self, collectionID, name, description, url,
        method, headers, data, dataMode):

        self.collectionId = collectionID
        self.id = str(uuid4())
        self.name = name
        self.description = description
        self.url = url
        self.method = method
        self.headers = headers
        self.data = data
        self.dataMode = dataMode
        self.timestamp = int(datetime.now().strftime("%s"))*1000

    def toJSON(self):
        return json.dumps(self.__dict__)


class PSCollection:
    def __init__(self, name):
        self.name = name
        self.id = str(uuid4())  # randomly generated guid
        self.timestamp = int(datetime.now().strftime("%s"))*1000
        self.requests = []

    def append(self, psrequest):
        self.requests.append(psrequest)

    def toJSON(self):
        temp_dict = {}
        for (key, value) in self.__dict__.iteritems():
            if type(value) == type([]):
                temp_dict[key] = []
                for val in value:
                    temp_dict[key].append(val.__dict__)
            else:
                temp_dict[key] = value

        return json.dumps(temp_dict)

def main():
    parser = argparse.ArgumentParser(description='Consume a Swagger-UI site and'+
        'produce JSON that can be imported into API testing tools.')
    parser.add_argument('url', metavar='url', type=str, nargs='+',
                   help='root of the Swagger json docs')
    args = parser.parse_args()

    try:
        r = requests.get(args.url[0])
    except:
        raise Exception("Resource not availible, check your VPN settings.")
    finally:
        if r.status_code == 200 and json.loads(r.content):
            api_root = json.loads(r.content)

            print("Located API. There are {} primary resources. Crawling each..."
                .format(len(api_root["apis"])))

            for resource in api_root["apis"]:
                print("Adding endpoints for {} resource."
                    .format(resource['path'][1:]))

                collection = PSCollection(resource['path'][1:])

                r = requests.get(args.url[0]+resource['path'])

                if r.status_code == 200 and json.loads(r.content):
                    api_resource = json.loads(r.content)
                    for endpoint in api_resource['apis']:
                        for operation in endpoint['operations']:
                            params = {}
                            for parameter in operation['parameters']:
                                params[parameter['name']] = parameter['description']
                            request = PSRequest(
                                collection.id,
                                operation['summary'],
                                operation['notes'],
                                api_resource['basePath'] + endpoint['path'],
                                operation['method'],
                                ["Accept: application/json", "Content-type: application/json"],
                                json.dumps(params),
                                "application/json"
                            )
                            collection.append(request)

                    with open("collections/{}.json".format(resource['path'][1:]), 'wb+') as f:
                        f.write(collection.toJSON())

                else:
                    raise Exception("No resource at specified URL")

            print("Done! Import the files in the 'collections' folder to Postman or Runscope.")

        else:
            raise Exception("No resource at specified URL")




if __name__ == "__main__":
    main()