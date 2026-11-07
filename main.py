import argparse, os, sys, yaml
import inspect

import walk
import food

def main():
    parser = argparse.ArgumentParser(description='dl playing bot')
    parser.add_argument("-j", "--job", help="Job type")
    parser.add_argument("-a", "--account", help="Account name")
    parser.add_argument("-s", "--start", help="start km")
    parser.add_argument("-f", "--finish", help="finish km")
    parser.add_argument("-i", "--index", help="key index")
    parser.add_argument("-c", "--count", help="key count")
    parser.add_argument("-p", "--pauses", help="list of pauses")
    parser.add_argument("-o", "--options", help="options")
    parser.add_argument("-q", "--quiet", help="quiet")
    args = parser.parse_args()

    name, api_id, api_hash = "", "", ""
    config = {}
    with open(os.path.join(sys.path[0], 'config.yaml'), 'r') as file:
        config = yaml.safe_load(file)

    for a in config.get('accounts'):
        if a.get('name') == args.account:
            name, api_id, api_hash = a.get('name'), a.get('api_id'), a.get('api_hash')

    if name == "" or api_id == "" or api_hash == "":
        print("Please enter account name and api_id and api_hash")
        return

    options = args.options.split(',') if args.options else []

    jobs = {
        "walk": walk.main,
        "food": food.main,
    }

    job = jobs.get(args.job)
    if job:
        sig = inspect.signature(job)
        data = {
            "name": name, "api_id": api_id, "api_hash": api_hash,
            "start": args.start, "finish": args.finish,
            "index": args.index, "count": args.count,
            "pauses": args.pauses, "quiet": args.quiet,
            "options": options,
        }
        filtered_args = {k: v for k, v in data.items() if k in sig.parameters}
        job(**filtered_args)
    else:
        print(f"Undefined job type {args.job}")


if __name__ == '__main__':
    main()
