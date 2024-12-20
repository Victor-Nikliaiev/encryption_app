##########################################################################
#### This key manager is used for generating RSA-4096 security level keys
##########################################################################

from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from backend.constants import Rsa
import logging

logging.basicConfig(level=logging.INFO)


class RsaKeyManager:

    def generate_private_key(self):
        """
        Generates a private RSA key for use with this key manager.

        :return: The generated private key
        """

        private_key = rsa.generate_private_key(
            public_exponent=Rsa.PUBLIC_EXPONENT,
            key_size=Rsa.KEY_SIZE,
            backend=default_backend(),
        )

        return private_key

    def generate_public_key(self, private_key: rsa.RSAPrivateKey) -> rsa.RSAPublicKey:
        """
        Generates a public RSA key from the given private key.

        :param private_key: An instance of RSAPrivateKey from which to derive the public key.
        :return: The corresponding RSAPublicKey.
        :raises TypeError: If the private_key is not an instance of RSAPrivateKey.
        """

        if not isinstance(private_key, rsa.RSAPrivateKey):
            raise TypeError("Private_key must be an instance of RSAPrivateKey")

        return private_key.public_key()

    def save_private_key_to_file(
        self, output_pem_file_path, password: str = None, private_key=None
    ):
        """
        Saves the given private RSA key to a specified PEM file path, optionally encrypting it with a password.

        :param private_key: The private RSA key to be saved.
        :param pem_file_path: The file path where the PEM-formatted private key will be saved.
        :param password: An optional password to encrypt the private key. If None, the key is saved without encryption.
        """
        if not private_key:
            private_key = rsa.generate_private_key(
                public_exponent=Rsa.PUBLIC_EXPONENT,
                key_size=Rsa.KEY_SIZE,
                backend=default_backend(),
            )

        encryption = (
            serialization.BestAvailableEncryption(password.encode("utf-8"))
            if password
            else serialization.NoEncryption()
        )
        with open(output_pem_file_path, "wb") as private_file:
            private_pem = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=encryption,
            )
            private_file.write(private_pem)
        logging.info(f"Private key saved to {output_pem_file_path}")

    def save_public_key_to_file(self, public_key, pem_file_path):
        """
        Saves the given public RSA key to a specified PEM file path.

        :param public_key: The public RSA key to be saved.
        :param pem_file_path: The file path where the PEM-formatted public key will be saved.
        """

        with open(pem_file_path, "wb") as public_file:
            public_pem = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            )
            public_file.write(public_pem)
        logging.info(f"Public key saved to {pem_file_path}")

    def load_private_key_from_file(self, pem_file_path, password: str = None):
        """
        Loads a private RSA key from a specified PEM file path, optionally decrypting it with a password.

        :param pem_file_path: The file path where the PEM-formatted private key is saved.
        :param password: An optional password to decrypt the private key. If None, the key is loaded without decryption.
        :return: The loaded private RSA key.
        """

        if password is not None:
            password = password.encode("utf-8")

        try:
            with open(pem_file_path, "rb") as private_file:
                private_key = serialization.load_pem_private_key(
                    private_file.read(), password=password, backend=default_backend()
                )
                logging.info(f"Private key loaded from {pem_file_path}")
                return private_key
        except FileNotFoundError:
            raise FileNotFoundError(f"Private key file not found: {pem_file_path}")
        except Exception as e:
            raise Exception(
                f"Failed to process private key. Please check file format and try again.\n\nAdditional Info:\n {e}"
            )

    def load_public_key_from_file(self, pem_file_path):
        """
        Loads a public RSA key from a specified PEM file path.

        :param pem_file_path: The file path where the PEM-formatted public key is saved.
        :return: The loaded public RSA key.
        """

        try:
            with open(pem_file_path, "rb") as public_file:
                public_key = serialization.load_pem_public_key(
                    public_file.read(), backend=default_backend()
                )
                logging.info(f"Public key loaded from {pem_file_path}")
                return public_key
        except FileNotFoundError:
            raise FileNotFoundError(f"Public key file not found: {pem_file_path}")
        except Exception as e:
            raise Exception(
                f"Failed to process public key. Please check file format and try again.\n\nAdditional Info:\n {e}"
            )

    def serialize_public_key(self, public_key: str):
        try:
            serialized_public_key = serialization.load_pem_public_key(
                public_key.encode("utf-8"), backend=default_backend()
            )
            return serialized_public_key
        except Exception as e:
            raise Exception(
                f"Failed to serialize public key, most likely key was corrupted, or you made a mistake, when provided the key.\nPlease check your input, and try again.\n\nAdditional Info:\n {e}"
            )

    def serialize_private_key(self, private_key: str, password: str):
        if password is not None:
            password = password.encode("utf-8")

        serialized_private_key = serialization.load_pem_private_key(
            private_key.encode("utf-8"), password=password, backend=default_backend()
        )
        return serialized_private_key
