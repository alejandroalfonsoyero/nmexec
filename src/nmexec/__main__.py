import os
from nmexec.server import Cluster


def main():
    cpus = os.cpu_count()
    if not isinstance(cpus, int):
        cpus = 1

    HOST = os.environ.get("HOST", "0.0.0.0")
    PORT = int(os.environ.get("PORT", 9786))

    cluster = Cluster(host=HOST, port=PORT)
    cluster.run(workers=cpus)


if __name__ == "__main__":
    main()
