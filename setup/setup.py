import sys, distro
from os import system
from colorama import Fore

#### verificacao da python-pip
try:
    import pip
except ImportError:
   if distro == 'debian' or distro == 'ubuntu':
       system("apt install python3-pip")
       import pip
   elif distro == 'arch':
       system("pacman -S python-pip")
       import pip
   else:
       print("instalar manual o pip... thg finalizado")
       exit(1)

try:
    import docker
except ImportError:
   if distro == 'debian' or distro == 'ubuntu':
       system("apt install docker.io")
       import docker
   elif distro == 'arch':
       system("pacman -S docker")
       import docker
   else:
       print("instalar manual o pip... thg finalizado")
       exit(1)

try:
    import apt
except ImportError:
    if distro == 'debian' or distro == 'ubuntu':
       system("apt install python3-apt")
       import apt
try:
    import pacman
except ImportError:
   if distro == 'arch':
       system("pip install python-pacman ")
       try:
          import pacman
       except ImportError:
          print("instalacao manual do python-pacman\nlink:https://pypi.org/project/python-pacman/")


'''
Instala os pacotes para o debian
'''


def arch_linux():
    import pacman
    # lista de programas
    listt = ['docker', "nmap"]
    # procura no cache
    pacman.refresh()
    banner = '''
████████╗██╗  ██╗ ██████╗        █████╗ ██████╗  ██████╗██╗  ██╗      ██╗███╗   ██╗███████╗████████╗ █████╗ ██╗     ██╗
╚══██╔══╝██║  ██║██╔════╝       ██╔══██╗██╔══██╗██╔════╝██║  ██║      ██║████╗  ██║██╔════╝╚══██╔══╝██╔══██╗██║     ██║
   ██║   ███████║██║  ███╗█████╗███████║██████╔╝██║     ███████║█████╗██║██╔██╗ ██║███████╗   ██║   ███████║██║     ██║
   ██║   ██╔══██║██║   ██║╚════╝██╔══██║██╔══██╗██║     ██╔══██║╚════╝██║██║╚██╗██║╚════██║   ██║   ██╔══██║██║     ██║
   ██║   ██║  ██║╚██████╔╝      ██║  ██║██║  ██║╚██████╗██║  ██║      ██║██║ ╚████║███████║   ██║   ██║  ██║███████╗███████╗
   ╚═╝   ╚═╝  ╚═╝ ╚═════╝       ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝      ╚═╝╚═╝  ╚═══╝╚══════╝   ╚═╝   ╚═╝  ╚═╝╚══════╝╚══════╝

    '''
    print(Fore.BLUE + banner)
    # faz o check dos programas
    for i in listt:
        if i in pacman.get_installed():
            print("{colorp}{i} =>{color} already installed".format(colorp=Fore.RED, color=Fore.CYAN, i=i))
        else:
            # instala
            try:
                pacman.install(i)
            except Exception as arg:
                print("Sorry, package installation failed [{err}]".format(err=str(arg)))


'''
Instala os pacotes para o debian
'''


def deb_ubu():
    # lista de programas
    listt = ['docker.io', "nmap"]
    # procura no cache
    cache = apt.cache.Cache()
    # atualiza o cache
    cache.update()
    cache.open()
    banner = '''
████████╗██╗  ██╗ ██████╗       ██╗   ██╗██████╗ ██╗   ██╗███╗   ██╗████████╗██╗   ██╗      ██╗███╗   ██╗███████╗████████╗ █████╗ ██╗     ██╗
╚══██╔══╝██║  ██║██╔════╝       ██║   ██║██╔══██╗██║   ██║████╗  ██║╚══██╔══╝██║   ██║      ██║████╗  ██║██╔════╝╚══██╔══╝██╔══██╗██║     ██║
   ██║   ███████║██║  ███╗█████╗██║   ██║██████╔╝██║   ██║██╔██╗ ██║   ██║   ██║   ██║█████╗██║██╔██╗ ██║███████╗   ██║   ███████║██║     ██║
   ██║   ██╔══██║██║   ██║╚════╝██║   ██║██╔══██╗██║   ██║██║╚██╗██║   ██║   ██║   ██║╚════╝██║██║╚██╗██║╚════██║   ██║   ██╔══██║██║     ██║
   ██║   ██║  ██║╚██████╔╝      ╚██████╔╝██████╔╝╚██████╔╝██║ ╚████║   ██║   ╚██████╔╝      ██║██║ ╚████║███████║   ██║   ██║  ██║███████╗███████╗
   ╚═╝   ╚═╝  ╚═╝ ╚═════╝        ╚═════╝ ╚═════╝  ╚═════╝ ╚═╝  ╚═══╝   ╚═╝    ╚═════╝       ╚═╝╚═╝  ╚═══╝╚══════╝   ╚═╝   ╚═╝  ╚═╝╚══════╝╚══════╝

    '''
    print(Fore.BLUE + banner)
    # faz o check dos programas
    for i in listt:
        pass
        pkg = cache[i]
        if pkg.is_installed:
            print("{colorp}{i} =>{color} already installed".format(colorp=Fore.RED, color=Fore.CYAN, i=i))
        else:
            # instala
            print(pkg.mark_install())
        try:
            cache.commit()
        except Exception as  arg:
            print("Sorry, package installation failed [{err}]".format(err=str(arg)))


'''
cria  e configura banco de dados
'''


def confpostgre():
    client = docker.from_env()
    try:
        img = client.images.get("postgres")
    except docker.errors.ImageNotFound:
        img = client.images.pull("postgres")

    try:
        container = client.containers.get("thgdb")
    except docker.errors.NotFound:
        container = None

    if img != None:
        if container != None:
            print("Database already exist!")
            container.start()
        else:
            print("Creating container...")
            client.containers.run("postgres", name="thgdb", environment={
                            "POSTGRES_PASSWORD": "thgdb",
                            "POSTGRES_USER": "thgdb",
                            "POSTGRES_DB": "thgdb",
                    }, ports={'5432/tcp': 5432}, detach=True)
            print("Container created!")



'''
Verifica a distro e configura o banco de dados
'''


def check():
    linux = distro.id()
    if linux == "ubuntu" or linux == "debian":
        deb_ubu()
        confpostgre()
    elif linux == "arch":
        arch_linux()
        confpostgre()
    else:
        print("Sorry, distro not found")
        pass
    print(Fore.RESET)


check()
