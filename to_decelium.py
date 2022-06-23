import sys
sys.path.append('../../../')
sys.path.append('../../')
sys.path.append('../')
class to_decelium():
    '''
    Simple wrapper which pushes code to decelium
    '''
    def remove(domain,
             app_dir,
             network_id,
             api_key,
             secret_password,
             file_path='index.html',remote=True):
        import paxdk.PaxFinancialAPI as paxdk
        pq = paxdk.PaxFinancialAPIClass(url_version= network_id ,api_key=api_key)
        '''
            Pushes to the server and throws an unintelligble tantrum if things dont go well.
        '''
        data  = pq.delete_entity({'api_key':api_key,'path':'/apps/'+app_dir+'/html_files/'+'index.html'},remote=remote)
        print("1",data)
        data  = pq.delete_entity({'api_key':api_key,'path':'/apps/'+app_dir+'/domains/'+domain},remote=remote)
        print("2",data)
    '''
    Simple wrapper which pushes code to decelium
    '''
    def push(domain,
             app_dir,
             network_id,
             api_key,
             secret_password,
             file_path='index.html',remote=True):
        import paxdk.PaxFinancialAPI as paxdk
        pq = paxdk.PaxFinancialAPIClass(url_version= network_id ,api_key=api_key)
        '''
            Pushes to the server and throws an unintelligble tantrum if things dont go well.
        '''
        data  = pq.delete_entity({'api_key':api_key,'path':'/apps/'+app_dir+'/html_files/'+'index.html'},remote=remote)
        print("1",data)
        data  = pq.delete_entity({'api_key':api_key,'path':'/apps/'+app_dir+'/domains/'+domain},remote=remote)
        print("2",data)
        with open(file_path,'r') as f:
            # '/apps/'+app_id+'/html_files/'+file_id
            res_obj =pq.create_entity({'api_key':api_key, 
                                       'path':'/apps/'+app_dir+'/html_files/', 
                                       'name':'index.html',
                                       'file_type':'file', 
                                       'payload':f.read(),},remote=remote)
            print("3",res_obj)
            assert 'obj-' in res_obj
            res_url =pq.create_entity({'api_key':api_key,
                                       'path':'/apps/'+app_dir+'/domains/',
                                       'name':domain,
                                       'file_type':'host',
                                       'attrib':{'host':domain,
                                                 'secret_password':secret_password,
                                                 'target_id':res_obj}
                                  },remote=remote)
            print("4",res_url)
            assert 'obj-' in res_url
            return True