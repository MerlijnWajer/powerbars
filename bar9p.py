import time
import py9p
import os

from barconfig import bars
#import signal

qid_to_socket = {}

class PowerBarFs(py9p.Server):
    def __init__(self):
        rootdir = py9p.Dir(0)    # not dotu
        rootdir.children = []
        rootdir.type = 0
        rootdir.dev = 0
        rootdir.mode = 0755 | py9p.DMDIR
        rootdir.atime = rootdir.mtime = int(time.time())
        rootdir.length = 0
        rootdir.name = '/'
        rootdir.uid = rootdir.gid = rootdir.muid = os.environ['USER']
        rootdir.qid = py9p.Qid(py9p.QTDIR, 0, py9p.hash8(rootdir.name))
        rootdir.parent = rootdir

        self.root = rootdir

        self.root.qid.file_obj = rootdir

        for bar in bars:
            print('Processing bar:', bar)
            for socket_name, socket in bar.sockets.items():
                print('Processing socket:', socket_name)

                nd = self._make_file(socket_name, self.root)
                self.root.children.append(nd)

                qid_to_socket[nd.qid] = (socket_name, socket)

    def _make_file(self, name, parent=None):
        newdir = py9p.Dir(0)    # not dotu
        newdir.children = []
        newdir.type = 0
        newdir.dev = 0
        newdir.mode = 0220
        newdir.atime = newdir.mtime = int(time.time())
        newdir.length = 0
        newdir.name = name
        newdir.uid = newdir.gid = newdir.muid = os.environ['USER']
        newdir.qid = py9p.Qid(0, 0, py9p.hash8(newdir.name))
        if parent:
            newdir.parent = parent
        else:
            newdir.parent = newdir

        newdir.qid.file_obj = newdir

        return newdir

    def stat(self, srv, req):
        req.ofcall.stat.append(req.fid.qid.file_obj)

        srv.respond(req, None)

    def read(self, srv, req):
        file_obj = req.fid.qid.file_obj

        if file_obj is self.root:
            req.ofcall.stat = self.root.children
        else:
            s = qid_to_socket[req.fid.qid]
            socket_name, socket = s
            print('Read on:', socket)

            to_return = '%s: %s\n' % (socket_name, socket.state)
            o = req.ifcall.offset
            c = req.ifcall.count

            req.ofcall.data = to_return[o:o+c]

        srv.respond(req, None)
        #srv.respond(None, 'funkenstein')

    def write(self, srv, req):
        file_obj = req.fid.qid.file_obj

        data = req.ifcall.data
        print('Write', data)


        s = qid_to_socket[req.fid.qid]
        socket_name, socket = s
        print('Read on:', socket)

        if data.strip() == 'On':
            socket.set_state(True)
        elif data.strip() == 'Off':
            socket.set_state(False)
        else:
            boom()

        req.ofcall.count = req.ifcall.count
        srv.respond(req, None)

    def wstat(self, srv, req):
        # ``honour'' wstat requests
        srv.respond(req, None)

    def walk(self, srv, req):
        '''
        Navigate the filesystem.
        '''

        search = req.ifcall.wname[0]
        for dirent in self.root.children:
            if search == dirent.name:
                req.ofcall.wqid = [dirent.qid]
                srv.respond(req, None)
                return

        # In walk apparently we may not return None as a request.
        srv.respond(req, 'No such file or directory')

#srv = py9p.Server(listen=('127.0.0.1', 9292), chatty=True)
srv = py9p.Server(listen=('0.0.0.0', 9292), chatty=False)
a = PowerBarFs()

srv.mount(a)
srv.serve()
