import sys
import argparse
import configparser
import logging
import os.path
from azure.storage.blob import BlobServiceClient, ContainerClient, BlobClient

# BlobServiceclient: Nous permet de manipuler les ressources de stockage Azure et les conteneurs blob.
# ContainerClient: Nous permet de manipuler les conteneurs de stockage Azure et leurs blobs.
# BlobClient : Nous permet de manipuler les blobs de stockage Azure.

#                           PENSEZ A REMPLIR LE FICHIER CONFIG.INI AVANT DE LANCER LES COMMANDES !
logging.basicConfig(
    filename="log_main.log",
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s - %(message)s',
    datefmt='%d/%m/%Y %H:%M:%S',)

def listb(args, containerclient):
    """
    Cette fonction nous retourne une liste de tout les éléments
    de notre stockage blob.
    Commande :py main.py list
    """
    blob_list=containerclient.list_blobs()
    for blob in blob_list:
        print(blob.name)


def upload(cible, blobclient):
    """
    Cette fonction nous permet d'uploader un fichier de notre pc 
    vers notre stockage blob.
    Commande :py main.py upload "route vers votre fichier"
    """
    with open(cible, "rb") as f:
        blobclient.upload_blob(f)


def download(filename, dl_folder, blobclient):
    """
    Cette fonction nous permet de telecharger un fichier de 
    notre stockage blob vers notre dossier locale.
    Commande :py main.py download "nom du blob à telecharger"
    """
    with open(os.path.join(dl_folder,filename), "wb") as my_blob:
        blob_data=blobclient.download_blob()
        blob_data.readinto(my_blob)


def main(args,config):
    """
    Cette fonction permet de prendre en compte les informations
    renseigné dans le fichier config.ini et de les réutiliser
    dans nos autres fonctions.
    """
    logging.info("Lancement de la fonction main")
    blobclient=BlobServiceClient(
        f"https://{config['storage']['account']}.blob.core.windows.net",
        config["storage"]["key"],
        logging_enable=False)
    logging.debug("Connexion au compte de stockage effectué")
    containerclient=blobclient.get_container_client(config["storage"]["container"])
    logging.debug("Connexion au container de stockage effectué")
    if args.action=="list":
        logging.debug("Lancement de la fonction liste")
        return listb(args, containerclient)
    else:
        if args.action=="upload":
            blobclient=containerclient.get_blob_client(os.path.basename(args.cible))
            logging.debug("Lancement de la fonction upload")
            logging.warning("Uploading du fichier")
            return upload(args.cible, blobclient)
        elif args.action=="download":
            logging.debug("Lancement de la fonction download")
            blobclient=containerclient.get_blob_client(os.path.basename(args.remote))
            logging.warning("Téléchargement du fichier")
            return download(args.remote, config["general"]["restoredir"], blobclient)
    

if __name__=="__main__":
    """
    C'est ici que sont définit nos différents arguments.
    """
    parser=argparse.ArgumentParser("Logiciel d'archivage de documents")
    parser.add_argument("-cfg",default="config.ini",help="chemin du fichier de configuration")
    parser.add_argument("-lvl",default="info",help="niveau de log")
    subparsers=parser.add_subparsers(dest="action",help="type d'operation")
    subparsers.required=True
    
    parser_s=subparsers.add_parser("upload")
    parser_s.add_argument("cible",help="fichier à envoyer")

    parser_r=subparsers.add_parser("download")
    parser_r.add_argument("remote",help="nom du fichier à télécharger")
    parser_r=subparsers.add_parser("list")

    args=parser.parse_args()

    #erreur dans logging.warning : on a la fonction au lieu de l'entier
    loglevels={"debug":logging.DEBUG, "info":logging.INFO, "warning":logging.WARNING, "error":logging.ERROR, "critical":logging.CRITICAL}
    logging.debug(loglevels[args.lvl.lower()])
    print(loglevels[args.lvl.lower()])
    logging.basicConfig(level=loglevels[args.lvl.lower()])

    config=configparser.ConfigParser()
    config.read(args.cfg)

    sys.exit(main(args,config))