from typing import Callable
from backend import signal_manager
from backend.chunk_encrypter import ChunkEncrypter
from backend.constants import Size
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey, RSAPrivateKey
import logging


from PySide6 import QtCore as qtc

from PySide6 import QtWidgets as qtw


from tools.toolkit import Tools as t


logging.basicConfig(level=logging.INFO)


class FileManager(qtc.QObject):

    def __init__(self):
        """
        Initializes FileManager with a ChunkEncrypter instance for encryption and decryption operations.

        :return: FileManager instance
        """
        super().__init__()

        self.chunk_encrypter: ChunkEncrypter
        self._stop_flag = False

        signal_manager.stop_process.connect(
            self.stop_process_request, qtc.Qt.DirectConnection
        )

    @qtc.Slot()
    def stop_process_request(self):
        self._stop_flag = True

    @qtc.Slot(str, str, RSAPublicKey)
    def encrypt_file(self, input_file_path: str, output_file_path: str, public_key):
        """
        Encrypts a given file using the ChunkEncrypter instance, writing the encrypted bytes to another file.

        :param input_file_path: The path to the file to be encrypted
        :param output_file_path: The path to the file where the encrypted bytes will be written
        """

        self.chunk_encrypter = ChunkEncrypter(public_key=public_key)

        self._process_file(
            input_file_path,
            output_file_path,
            self.chunk_encrypter.encrypt_chunk,
            Size.ENCRYPTION_CHUNK,
        )

    @qtc.Slot(str, str, RSAPrivateKey)
    def decrypt_file(self, input_file_path: str, output_file_path: str, private_key):
        """
        Decrypts a given file using the ChunkEncrypter instance, writing the decrypted bytes to another file.

        :param input_file_path: The path to the file to be decrypted
        :param output_file_path: The path to the file where the decrypted bytes will be written
        """

        self.chunk_encrypter = ChunkEncrypter(private_key=private_key)

        self._process_file(
            input_file_path,
            output_file_path,
            self.chunk_encrypter.decrypt_chunk,
            Size.DECRYPTION_CHUNK,
        )

    def _process_file(
        self,
        input_file_path: str,
        output_file_path: str,
        chunk_handler: Callable[[bytes], bytes],
        chunk_size: int,
    ):
        """
        Reads a given file chunk by chunk, processes each chunk using a given callable, and writes the processed chunks to another file.

        :param input_file_path: The path to the file to be read
        :param output_file_path: The path to the file where the processed chunks will be written
        :param chunk_handler: The callable to be used to process the chunks
        :param chunk_size: The size of the chunks to be read and processed
        """
        try:
            with open(input_file_path, "rb") as infile, open(
                output_file_path, "wb"
            ) as outfile:
                while True:
                    if self._stop_flag:
                        print("Process stopped by user.")
                        return
                    chunk = infile.read(chunk_size)

                    if not chunk:  # If end of file
                        break

                    processed_chunk = chunk_handler(chunk)
                    outfile.write(processed_chunk)
                    signal_manager.update_processed_bytes.emit(len(chunk))

                signal_manager.operation_completed.emit()

        except Exception as e:
            logging.error(f"Error processing file {input_file_path}: {e}")
            # qtw.QMessageBox.critical(
            #     None, "Error", f"Error processing file: {input_file_path}, {e}"
            # )
            signal_manager.critical_error.emit(input_file_path, str(e))
