#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
import socket
import pickle
from queue import Queue
from threading import Thread
import tempfile
from . import transact


class Master():
	"""A class that handles multi processing"""
	def __init__(self, n):
		"""module is a string with the name of the modulel where the
		functions you are going to run are """

		self.fpath = os.path.join(tempfile.gettempdir(),'mp')
		os.makedirs(self.fpath, exist_ok=True)
		self.n_slaves = n
		self.slaves=[slave() for i in range(n)]
		self.q = Queue()
		self.active_processes = 0
		pids=[]
		for i in range(n):
			self.slaves[i].confirm(i) 
			pid=str(self.slaves[i].p_id)
			if int(i/5.0)==i/5.0:
				pid='\n'+pid
			pids.append(pid)

		pstr="""Multi core processing enabled using %s cores. \n
Master PID: %s \n
Slave PIDs: %s"""  %(n,os.getpid(),', '.join(pids))
		print (pstr)

	def send_dict(self, d):
		f = tempfile.NamedTemporaryFile()
		fname = f.name
		f.close()
		f = open(fname,'wb')
		pickle.dump(d,f)
		f.close()
		for s in self.slaves:
			s.send('dict',fname)
			t=Thread(target=s.receive,args=(self.q,), daemon=True)
			t.start()
			self.active_processes += 1
		#threading.Thread(target=delayed_close, args=(fname,)) 

		a=0
		
			
	def quit(self):
		for i in self.slaves:
			i.p.stdout.close()
			i.p.stderr.close()
			i.p.stdin.close()
			i.p.kill()
			i.p.wait()
			

	def run(self, tasks, operation):
		"""tasks is a list of string expressions to be executed. All variables in expressions are stored 
		in the dictionary sent to the slaves"""
		self.collect()
		if type(tasks) == str:
			tasks = [tasks]*self.n_slaves
		for i in range(len(tasks)):
			s = self.slaves[i]
			s.send(operation, tasks[i])#initiating the self.cpus first evaluations
			t=Thread(target=s.receive,args=(self.q,), daemon=True)
			t.start()
			self.active_processes += 1

	def exec(self, task):
		return self.run(task, 'exec')

	def eval(self, task):
		self.run(task, 'eval')

	def collect(self, force_quit = False):
		"""Waiting and collecting the sent tasks. """
		d = {}
		t = time.time()
		MAXTIME = 8
		while self.active_processes>0:
			try:
				if force_quit:
					dt = time.time()-t
					ds,s = self.q.get(timeout=max((MAXTIME-dt,1)))
				else:
					ds,s = self.q.get()
				self.active_processes -= 1
				if isinstance(ds, BaseException):
					raise ds
				d[s] = ds	
			except Exception as e:
				print(e)
				if force_quit:
					for s in range(len(self.slaves)):
						if not s in d:
							self.slaves[s].kill()
		return d

class slave():
	"""Creates a slave"""
	command = [sys.executable, "-u", "-m", "paneltime_mp.slave"]


	def __init__(self):
		"""Starts local worker"""
		self.p = subprocess.Popen(self.command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		self.t=transact.Transact(self.p.stdout,self.p.stdin, False)
		self.connected = False
		
	def confirm(self,slave_id):
		self.p_id = self.receive()
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.slave_id=slave_id
		self.send('init_transact',slave_id)
		self.host = self.receive()
		self.send('OK',None)
		pass

	def send(self,msg,obj):
		"""Sends msg and obj to the slave"""
		if not self.p.poll() is None:
			raise RuntimeError('process has ended')
		self.t.send((msg,obj))     

	def receive(self,q=None):

		if q is None:
			answ=self.t.receive()
			return answ
		try:
			q.put((self.t.receive(),self.slave_id))
		except Exception as e:
			q.put((e,self.slave_id))

	def connect(self):
		if self.connected:
			return
		for i in range(100):
			try:
				self.socket.connect(self.host)
				self.connected = True
				break
			except ConnectionRefusedError:
				pass

	def kill(self):
		self.connect()
		self.socket.sendall(b"STOP")

			





import threading
import time

def delayed_close(fname):
	i=0
	for i in range(200):
		i+=1
		try:
			time.sleep(1)  # Thread sleeps here, minimal resource usage
			os.remove(fname)        # Close the file after the delay
			print(f"{fname} closed at iteration {i}")
		except:
			pass
		
