import os
import base64
print(os.getcwd())
from os import listdir
from os.path import isfile, join
import subprocess,json
from jsmin import jsmin

class build():
    def __init__(self,base_dir='.'):
        self.base_dir = base_dir
    '''
    Compress an entire website into one single file.
    '''
    def create_png_js(self,file):
        file_beginning = file.split('.')[0]
        file_ending = file.split('.')[1]
        if file_ending =='png':
            print('building.. ',file_beginning)
        else:
            return
        with open(self.base_dir+'/assets/raw/'+file,'rb') as f:
            encoded_string = base64.b64encode(f.read())
            with open(self.base_dir+'/assets/'+file_beginning+'.js','w') as f:
                f.write('''define([],function(){
                    data = "'''+encoded_string.decode('utf-8')+'''";
                    return {
                    "base64":data,
                    "src":"data:image/png;base64,"+data
                            }
                    });''');
    def create_jpg_js(self,file):
        file_beginning = file.split('.')[0]
        file_ending = file.split('.')[1]
        if file_ending =='jpg':
            print('building.. ',file_beginning)
        else:
            return
        with open(self.base_dir+'/assets/raw/'+file,'rb') as f:
            encoded_string = base64.b64encode(f.read())
            with open(self.base_dir+'/assets/'+file_beginning+'.js','w') as f:
                f.write('''define([],function(){
                    data = "'''+encoded_string.decode('utf-8')+'''";
                    return {
                    "base64":data,
                    "src":"data:image/jpeg;base64,"+data
                            }
                    });''');
                
    def create_json_js(self,file):
        file_beginning = file.split('.')[0]
        file_ending = file.split('.')[1]
        if file_ending =='json':
            print('building.. ',file_beginning)
        else:
            return
        with open(self.base_dir+'/assets/raw/'+file,'r') as f:
            encoded_string = f.read()
            with open(self.base_dir+'/assets/'+file_beginning+'.js','w') as f:
                f.write('''define([],function(){return '''+encoded_string+''';});''');
            
    def generate_all_images(self):
        try:
            [self.create_png_js(file) for file in listdir(self.base_dir+'/assets/raw/')]
        except:
            print("could not assets to compress in "+self.base_dir+'/assets/raw/')
        try:
            [self.create_jpg_js(file) for file in listdir(self.base_dir+'/assets/raw/')]
        except:
            print("could not assets to compress in "+self.base_dir+'/assets/raw/')
    def generate_all_json(self):
        try:
            [self.create_json_js(file) for file in listdir(self.base_dir+'/assets/raw/')]
        except:
            print("could not assets to compress in "+self.base_dir+'/assets/raw/')
    def generate_configuration(self,file_name,data):
        with open(self.base_dir+'/'+file_name,'w') as f:
            f.write('''
            define([],function(){
            return '''+json.dumps(data)+'''});        
            ''')

    def build_website(self):
        #print(__file__.replace('build.py',''))
        print(__file__.replace('build.py',''))
        root_dir = '/usr/bin/js '+__file__.replace('build.py','')+'r.js -o '+self.base_dir+'/build.js'
        print(subprocess.run(root_dir.split(' '), capture_output=True).stdout)
        with open(self.base_dir+'/main-built.js') as js_file:
            raw_js = js_file.read()        
            with open(self.base_dir+'/test_index.html','w') as f:
                html = '''
                <!DOCTYPE html>
                <html >
                    <head>
                        <script src="https://requirejs.org/docs/release/2.3.6/minified/require.js"></script>  
                        <script src ='main-built.js' ></script> 
                    </head>
                    <body  class="bg-gray-900"  style="font-family:'Roboto', sans-serif;" >
                    </body>
                </html>                
                '''
                f.write(html);
            minified = jsmin(raw_js)        
            with open(self.base_dir+'/index.html','w') as f:
                html = '''
                <!DOCTYPE html>
                <html >
                    <head>
                        <script src="https://requirejs.org/docs/release/2.3.6/minified/require.js"></script>  
                        <script >'''+raw_js+'''</script> 
                    </head>
                    <body  class="bg-gray-900"  style="font-family:'Roboto', sans-serif;" >
                    </body>
                </html>                
                '''
                f.write(html);
    def run(self,file_name=None,data=None):
        if file_name and data:
            self.generate_configuration(file_name,data)
        self.generate_all_images();
        self.generate_all_json();
        self.build_website();
