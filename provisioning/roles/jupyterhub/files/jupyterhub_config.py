# Configuration file for Jupyter Hub

c = get_config()

c.JupyterHub.bind_url = "https://128.232.124.216:443/"

from dockerspawner import DockerSpawner

class VolumeCreatingSpawner(DockerSpawner):
    """
    DockerSpawner, but creates volumes
    """

    def start(self):
        directory = "/opt/jupyterhub/volumes/" + self.user.name
        if not os.path.exists(directory):
            os.makedirs(directory)
            os.chown(directory,1000,1000)
        return super().start()


# spawn with Docker
c.JupyterHub.spawner_class = VolumeCreatingSpawner
c.DockerSpawner.image = 'jonludlam/owl-jupyter'

notebook_dir = "/home/opam/work"
c.DockerSpawner.notebook_dir = notebook_dir
c.DockerSpawner.volumes = { '/opt/jupyterhub/volumes/{username}': notebook_dir }

# The docker instances need access to the Hub, so the default loopback port doesn't work:
from jupyter_client.localinterfaces import public_ips
c.JupyterHub.hub_ip = public_ips()[0]

# OAuth with GitHub
from raven_auth.raven_auth import RavenAuthenticator
c.JupyterHub.authenticator_class = RavenAuthenticator

c.RavenAuthenticator.description="OwlServer"
c.RavenAuthenticator.long_description="Owl Jupyter Server"
c.RavenAuthenticator.login_logo="/opt/jupyterhub/origami-camel.png"
c.RavenAuthenticator.ssl=True

c.Authenticator.whitelist = whitelist = set()
c.Authenticator.admin_users = admin = set()

import os

join = os.path.join
here = os.path.dirname(__file__)
with open(join(here, 'userlist')) as f:
    for line in f:
        if not line:
            continue
        parts = line.split()
        name = parts[0]
        whitelist.add(name)
        if len(parts) > 1 and parts[1] == 'admin':
            admin.add(name)

# ssl config
ssl = '/etc/letsencrypt/live/hub.ocamllabs.io'
keyfile = join(ssl, 'privkey.pem')
certfile = join(ssl, 'fullchain.pem')
if os.path.exists(keyfile):
    c.JupyterHub.ssl_key = keyfile
if os.path.exists(certfile):
    c.JupyterHub.ssl_cert = certfile

