#!/usr/bin/env python3
#@hecsv17/Hamza
import requests, json, argparse, re, os, multiprocessing, subprocess

print('''
   CCrawlEN v1.0
        Author: @hecvs17 -Hamza-
''')

parser = argparse.ArgumentParser()
parser.add_argument('domain', help = 'Target domain to lookup', type = str)
args = parser.parse_args()
Target = args.domain


cmd = "mkdir "+Target+""
subprocess.call(cmd, shell=True)
currentDir = os.getcwd()


name = currentDir+"/"+Target+"/"+"urls-"+Target+".txt"
def saveToFile(url):
	with open(name,"a+") as f:
    		f.write(url+"\n")
	

notdup = currentDir+"/"+Target+"/"+"unikUrls"+Target+".txt"
def removeDuplicate(fp,fs):
	lines_seen = set() # holds lines already seen
	outfile = open(fp, "a+")
	for line in open(fs, "r+"):
    		if line not in lines_seen: # not a duplicate
        		outfile.write(line)
        		lines_seen.add(line)
	outfile.close()
nsubs = currentDir+"/"+Target+"/"+"tempNumbers-"+Target+".txt"
number_subs = currentDir+"/"+Target+"/"+"totalSubs-"+Target+".txt"
def numberOfSubs():
	c_outfile = open(nsubs,"a+")
	for line in open(notdup,"r"):
		cline = line.split("/")[2]
		c_outfile.write(cline+"\n")
	removeDuplicate(number_subs,nsubs)
	num_lines = sum(1 for line in open(number_subs))
	print('\n[+] In total {0} unique subdomains were retrieved.'.format(num_lines))
	for sub in open(number_subs):
		print('Subdomain found: {0}'.format(sub.strip()))
	

juicy = currentDir+"/"+Target+"/"+"juicyEnds-"+Target+".txt"
def findJuicyEndpoints():
	outfile = open(juicy,"a+")
	#Feel free to add your keywords here
	for line in open(notdup, "r"):
		if "url" in line or "redirect" in line or "redirect_url" in line or "redirectUrl" in line or "return" in line or "return_url" in line or "return_uri" in line or "next" in line or "next_url" in line or "goto" in line or "image=" in line or "fetch" in line or "target" in line or ".sql" in line or "filename" in line or "file=" in line:
			outfile.write(line)
	outfile.close()
jsfiles = currentDir+"/"+Target+"/"+"jsFiles-"+Target+".txt"
def findJSfiles():
	outfile = open(jsfiles, "a+")
	lines_seen = set()
	for line in open(notdup,"r"):
		if ".js" in line:
			if line not in lines_seen:
				outfile.write(line)
				lines_seen.add(line)
	outfile.close()

def getLinks(CdxApi, IndexNum):
	print("Processing {0}".format(IndexNum))
	Req = requests.get(CdxApi+'?url='+Target+'&fl=url&matchType=domain&pageSize=2000&output=json')
	Ans = Req.text.split('\n')[:-1]
	try:
		for entry in Ans:
			Url = json.loads(entry)['url']
			Domains =  re.findall(r'(?<=://)[^/|?|#]*', Url)[0]
			saveToFile(Url)
		print("{0} Processed".format(IndexNum))
	except:
		pass

def getIndexFile():
	IndexURL = "https://index.commoncrawl.org/collinfo.json"
	Data = requests.get(IndexURL).text
	Indexes = json.loads(Data)
	threads = []
	print("You have %s CPUs...\nLet's use them all!"%multiprocessing.cpu_count())
	Pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())
	for res in Indexes:
		proc = Pool.apply_async(getLinks, (res['cdx-api'],(res['id'])))
		threads.append(proc)
	for proc in threads:
		proc.get()



def main():
	getIndexFile()
	removeDuplicate(notdup,name)
	numberOfSubs()
	findJuicyEndpoints()
	findJSfiles()
	os.remove(nsubs)
if __name__ == '__main__':
	main()
