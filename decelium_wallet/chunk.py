# build(from_path,to_path):    
# extract(from_path,to_path):    
import shutil, os, base64
from zipfile import ZipFile
import time
class Chunk:
    tmp_file = "temp_zip.zip"
    def obliterate(path):
        commands = [os.remove,os.rmdir,shutil.rmtree]
        for c in commands:
            try:
                c(path)
                return True
            except:
                pass
        raise Exception("could not remove object")
            
    def build(from_path,to_path):    
        Chunk.build_zip(from_path,Chunk.tmp_file)
        Chunk.build_chunks(Chunk.tmp_file,to_path)
        Chunk.obliterate(Chunk.tmp_file)
    
    def extract(from_path,to_path):    
        Chunk.extract_chunks(from_path,"extract_"+Chunk.tmp_file)
        Chunk.extract_zip("extract_"+Chunk.tmp_file,to_path)
        Chunk.obliterate("extract_"+Chunk.tmp_file)
    
    def build_zip(from_path,to_file):
        #print(from_path)
        shutil.make_archive(to_file.replace(".zip",""), 'zip', from_path)
        remote=True
    
    def build_chunks(from_file,to_path):
        file_number = 0            
        sz = 2*1024*1024
        try:
            os.mkdir(to_path)
        except:
            pass
        
        with open(from_file,'rb') as f:
            bts = f.read()
            encoded = base64.b64encode(bts).decode("ascii") 
            while file_number*sz < len(encoded):
                dest_path = (to_path+'/chunk_' + str(file_number)).replace("//","/")
                with open(dest_path,'w') as chunk_file:
                    chunk_file.write(encoded[file_number*sz:(file_number+1)*sz])
                    file_number = file_number + 1
                assert file_number < 30
                
    def extract_chunks(from_path,to_file):
        ## reassebble the file.
        #print("reassebble the file.")
        complete_file = ""
        file_number = len([name for name in os.listdir(from_path)])
        #print(os.listdir(from_path))
        #print(from_path)
        #print(file_number)
        for file_index in range(0,file_number):
            dest_path = (from_path+'/chunk_' + str(file_index)).replace("//","/")
            #print(dest_path) 
            #print(os.path.getsize(dest_path)) 
            with open(dest_path,'r') as chunk_in:
                #print(dest_path)
                chunk = chunk_in.read()
                #print(len(chunk))
                complete_file = complete_file + chunk.strip()
                assert file_index < 30
        encoded_b = complete_file.encode("ascii")
        bts = base64.b64decode(encoded_b)  
        #print("reassebble the file.3"+to_file)
        with open(to_file,'wb') as f:
            f.write(bts)
            f.close()
        return True
    
    def extract_zip(from_file,to_path):
        with ZipFile(from_file, 'r') as zipObj:
            zipObj.extractall(to_path)     
        
            
    def upload(pq,api_key,remote,from_path,remote_path,extract_path = "chunk_test"):        
        #print("Starts Here")
        
        Chunk.build(from_path,extract_path)    
        #print("Also Also Not Ends  Here")
        chunks = pq.list({'api_key':api_key, 'path':remote_path, },remote=remote)
        #print("Also Not Ends  Here")
        
        if 'error' not in chunks:
            for fileobj in chunks:        
                fil  = pq.delete_entity({'api_key':api_key,  'path':remote_path, 'name':fileobj['dir_name'], },remote=remote)
        fil  = pq.delete_entity({'api_key':api_key,  'path':remote_path,},remote=remote) # show_url=True to debug
        
        dir_obj_id  = pq.create_directory({
            'api_key':api_key,
            'path':remote_path,},remote=remote)
        

        chunks = [name for name in os.listdir(extract_path)]
        for filename in chunks:
            t = time.time()
            #print("DOING DELETE")
            fil  = pq.delete_entity({'api_key':api_key, 
                                    'path':remote_path, 
                                    'name':filename, 
                                    },remote=remote) # show_url=True to debug
            #print(fil)
            
            delay = (time.time() - t)
            #print("END DOING DELETE"+ str(delay))
            with open(extract_path+"/"+filename,'r') as f:
                t = time.time()
                #print("DOING CREATE")

                fil  = pq.create_entity({
                    'api_key':api_key,
                    'path':remote_path,
                    'name':filename,
                    'file_type':'ipfs',
                    'payload':f.read()},remote=remote)
                #t = time.time()
                #print("DOING CREATE")
                delay = (time.time() - t)
                #print("END DOING CREATE "+str(delay))

                #print(fil)
                assert 'obj' in fil
        Chunk.obliterate(extract_path)
        
        
        
        return dir_obj_id

                
        
    def download(pq,api_key,remote,remote_path,to_path,extract_path="chunk_test",unpack=True,keep_raw=False):
        if 'obj' in remote_path or 'dir' in remote_path  :
            chunks = pq.list({'api_key':api_key, 'self_id':remote_path, },remote=remote)
        else:
            chunks = pq.list({'api_key':api_key, 'path':remote_path, },remote=remote)
        #print("-------------------CHUNKS")
        #print(chunks)
        try:
            os.mkdir(extract_path+"_downloaded")
        except:
            pass        
        for fileobj in chunks:
            #print("downloaded "+ fileobj['self_id'])
            
            #data  = pq.download_entity({'api_key':api_key,'self_id':fil , 'attrib':True},remote=remote)
            ent = pq.download_entity({'api_key':api_key,'self_id':fileobj['self_id']},remote=remote,show_errors=True)
                
            if 'error' in ent and type(ent) == dict:
                print(" WE HAVE AN ERROR")
                print(fileobj)
                raise Exception(str(ent))
            with open(extract_path+"_downloaded"+"/"+fileobj['dir_name'],'w') as f:
                f.write(ent)
            #fil  = pq.delete_entity({'api_key':api_key, 
            #                        'path':remote_path, 
            #                        'name':filename, 
            #                        },remote=remote) # show_url=True to debug
            #assert fil==True
        if unpack == True:
            Chunk.extract(extract_path+"_downloaded",to_path)    
        else:
            Chunk.extract_chunks(extract_path+"_downloaded",to_path)
        if keep_raw == False:
            Chunk.obliterate(extract_path+"_downloaded")

        