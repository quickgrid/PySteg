import numpy as np
from scipy.io.wavfile import write
from PIL import Image
import soundfile as sf
import os
import StegAppFrameSplitter as safp
import StegAppFrameJoiner as safj
import time
import hashlib
import math
import shutil


class ZipToImage3:

    def __init__(self, *args, **kwargs):
        self.self_ref = args[0]
        self.file_directorty = args[1]

        if len(kwargs) is not 0:
            self.width = kwargs['width']
            self.height = kwargs['height']
            self.file_size = os.path.getsize(self.file_directorty)
            self.RGB = 3
            self.piece_count =  math.ceil(int(self.file_size) / (self.RGB * int(self.width) * int(self.height)))
            self.increment_percentage = 100 / int(self.piece_count)

        self.setFolderDirectory()


    def setFolderDirectory(self):
         limit_index = self.file_directorty.rindex('\\')
         self.folder_directory = self.file_directorty[:limit_index + 1]

        
    def printDir(self):
        print(self.file_directorty)

        
    def getResolution(self):
        print(self.width, self.height)

        
    def splitFile(self):
        CHUNK_SIZE = 3 * int(self.width) * int(self.height) - 1

        #print(CHUNK_SIZE)

        file_number = 0
        gauge_value = 0
        piece_number = 0

        with open(self.file_directorty, 'rb') as fl:

            out_filename = os.path.basename(self.file_directorty)
            #out_filename = out_filename.rpartition('.')[0]

            b = True
            while b:
                b = fl.read(CHUNK_SIZE)
                if not b: break

                tmp_dir = os.path.join(self.folder_directory, 'output', '')
                if not os.path.exists(tmp_dir):
                    os.makedirs(tmp_dir)

                fout = open(tmp_dir + out_filename + "." + str(file_number) + ".zti", "wb")
                fout.write(b)
                fout.close()
                file_number += 1

                gauge_value += self.increment_percentage
                piece_number += 1
                safp.StegAppFrameSplitter.gauge_updater(self.self_ref, gauge_value, piece_number)
                
        return 0



    def convertToImage(self):

        gauge_value = 0
        safp.StegAppFrameSplitter.gauge_updater(self.self_ref, gauge_value, -1)

        path = os.path.join(self.folder_directory, 'output', '')
        fileList = sorted(os.listdir(path), key=len)

        new_path = os.path.join(self.folder_directory, 'generated_images', '')
        if not os.path.exists(new_path):
            os.makedirs(new_path)

        #print(fileList)
        #print(len(fileList))

        psteg_writer = "#@PySteg"

        filename = self.file_directorty
        sha256_hash = hashlib.sha256()
        with open(filename, "rb") as f:
            # Read and update hash string value in blocks of 4K
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
            print(sha256_hash.hexdigest())
            psteg_writer += '\n' + sha256_hash.hexdigest()

        increment_amount = 100 / len(fileList)
        piece_number = 0
        gauge_value = 0
        safp.StegAppFrameSplitter.gauge_updater(self.self_ref, gauge_value, -1)

        binary_file_integers = []
        for i in range(0, len(fileList) - 1):
            list_int = []
            #print(fileList)

            with open(path + fileList[i], 'rb') as fl:
                print(path + fileList[i])

                b = True
                while b:
                    b = fl.read(1)
                    tmp = int.from_bytes(b, byteorder="little", signed=True)
                    list_int.append(tmp)

            binary_file_integers = np.array(list_int)
            binary_file_integers = np.int8(binary_file_integers)

            print(len(binary_file_integers))

            #print(fileList[i])
            data = np.reshape(binary_file_integers, (int(self.height), int(self.width), int(self.RGB)))

            img = Image.fromarray(data, 'RGB')

            piece_number += 1
            gauge_value += increment_amount
            safp.StegAppFrameSplitter.gauge_updater(self.self_ref, gauge_value, piece_number)

            out_filename = fileList[i].rpartition('.')[0]
            img.save(new_path + out_filename + '.zti.png')

            psteg_writer += '\n' + out_filename + '.zti.png'
            #print(new_path + 'img ' + str(i) +  '.zti.png')

        try:
            last_file = len(fileList) - 1
            list_int = []
            with open(path + fileList[last_file], 'rb') as fl:
                print(path + fileList[last_file])

                b = True
                while b:
                    b = fl.read(1)
                    tmp = int.from_bytes(b, byteorder="little", signed=True)
                    list_int.append(tmp)

            binary_file_integers = np.array(list_int)
            binary_file_integers = np.int8(binary_file_integers)

            data = np.reshape(binary_file_integers, (int(self.height), int(self.width), int(self.RGB)))

            img = Image.fromarray(data, 'RGB')

            out_filename = fileList[last_file].rpartition('.')[0]
            img.save(new_path + out_filename + '.zti.png')

            psteg_writer += '\n' + out_filename + '.zti.png'

        except:
            shutil.copy(path + fileList[-1], new_path)
            psteg_writer += '\n' + fileList[-1]

            print("ERROR IN LAST FILE SIZE")

        with open(new_path + fileList[0].rpartition('.')[0] + '.psteg', 'w') as data:
            data.write(psteg_writer)

        gauge_value = 100
        safp.StegAppFrameSplitter.gauge_updater(self.self_ref, gauge_value, -3)

        print("WORK DONE")
        return 0


    def assembleFile(self):

        path = os.path.join(self.folder_directory, 'generated_images', '')

        # Get all the file names in directory

        fileList = []
        f = [f for f in os.listdir(path) if f.endswith('.psteg')]
        print(f)
        with open(path + f[0], "r") as myfile:

            val = myfile.readline()
            val = val.strip('\n')
            #print(val)

            if val != '#@PySteg':
                return -1

            global file_hash_sha256
            file_hash_sha256 = myfile.readline()

            for line in myfile:
                fileList.append(line.strip('\n'))
            print(fileList)

        new_fileList = fileList[:-1]
        print(new_fileList)

        increment_amount = 100 / len(fileList)
        piece_number = 0
        gauge_value = 0

        list_inv = []
        for file in new_fileList:
            im = Image.open(path + file)
            np_im = np.array(im)
            np_im = np_im.ravel()
            np_im = np.int8(np_im)

            #print("AT " +  file)
            for i in range(len(np_im) - 1):
                list_inv.append(int(np_im[i]).to_bytes(1, byteorder="little", signed=True))

            gauge_value += increment_amount
            piece_number += 1
            safj.StegAppFrameJoiner.gauge_updater(self.self_ref, gauge_value, piece_number)

        print("half done")
        print(len(list_inv))

        tmp = fileList[-1].rpartition('.')[0]
        tmp = tmp.rpartition('.')[0]
        # Write the byte data to new file

        global img_out_path
        img_out_path = path + tmp

        with open(path + tmp, 'wb') as f:
            f.writelines(list_inv)

        print("wrote file")

        with open(path + tmp, "ab") as myfile, open(path + fileList[-1], "rb") as file2:
            myfile.write(file2.read())

        print("ALL DONE")

        gauge_value = 100
        safj.StegAppFrameJoiner.gauge_updater(self.self_ref, gauge_value, -3)

        return 0


    def calculateHash(self):
        newfile_hash = ''

        filename = img_out_path
        sha256_hash = hashlib.sha256()
        with open(filename, "rb") as f:
            # Read and update hash string value in blocks of 4K
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
            newfile_hash = sha256_hash.hexdigest()

        print(file_hash_sha256)
        print(newfile_hash)

        if(file_hash_sha256.strip('\n') == newfile_hash):
            print("Success")
            return 0
        else:
            print("File Corrupted")
            return -1
