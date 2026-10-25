import subprocess,json,select
class Client:
 def __init__(self):
  self.p=subprocess.Popen(['/home/pepsi2/.local/opt/solidcraft/0.22.0/bin/solidcraft-cli','mcp','--headless','--allow-path','/home/pepsi2/dito/3dmodel'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=open('/tmp/sc-stderr.log','w'),text=True);self.i=0
  self.call('initialize',{'protocolVersion':'2025-06-18','capabilities':{},'clientInfo':{'name':'keychain-builder','version':'1'}})
  self.p.stdin.write('{"jsonrpc":"2.0","method":"notifications/initialized"}\n');self.p.stdin.flush()
 def call(self,m,p):
  self.i+=1;self.p.stdin.write(json.dumps(dict(jsonrpc='2.0',id=self.i,method=m,params=p))+'\n');self.p.stdin.flush()
  if not select.select([self.p.stdout],[],[],180)[0]:raise RuntimeError('timeout')
  r=json.loads(self.p.stdout.readline())
  if 'error'in r:raise RuntimeError(r)
  r=r['result']
  if r.get('isError'):raise RuntimeError(r)
  return r
 def tool(self,n,a={}):return self.call('tools/call',{'name':n,'arguments':a})
 def execute(self,c,p={}):return self.tool('execute',{'command':c,'params':p,'verbose':False})
if __name__=='__main__':
 c=Client()
 for name in ['sketch.line','sketch.spline','sketch.text','file.import_svg','solid.combine']:
  print(name,json.dumps(c.tool('describe_command',{'id':name}),ensure_ascii=False))
 print('export',json.dumps([t for t in c.call('tools/list',{})['tools'] if t['name'] in ['export','save','screenshot']],ensure_ascii=False))
 c.p.terminate()
